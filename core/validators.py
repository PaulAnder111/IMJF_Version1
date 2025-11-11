import re
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError


# Mapping of models -> their contact field names for email/telephone
# Keys are '<app_label>.<ModelName>'
CONTACT_FIELD_MAP = {
    'utilisateurs.CustomUser': {'email': 'email', 'telephone': 'telephone'},
    'enseignants.Enseignant': {'email': 'email', 'telephone': 'telephone'},
    'inscriptions.Inscription': {'email': 'email_responsable', 'telephone': 'telephone_responsable'},
}


def _normalize_phone(value: str) -> str:
    if not value:
        return ''
    # Keep only digits
    digits = re.sub(r"\D", "", str(value))
    return digits


def validate_phone_prefix(value: str):
    """Validate that the phone number belongs to allowed operators (Digicel/Natcom).

    Behavior:
    - Normalizes the number by stripping non-digits.
    - Accepts numbers that start with country code '509' or local 8-digit numbers.
    - Checks the leading operator prefix against allowed prefixes defined in
      settings.PHONE_ALLOWED_PREFIXES (list of strings). If not set a reasonable
      default is used.

    NOTE: Default prefixes are conservative common mobile prefixes. If you want
    exact operator prefixes for your country, set PHONE_ALLOWED_PREFIXES in
    your Django settings (e.g. ["34","35","36","37","38","39"]).
    """
    digits = _normalize_phone(value)
    if not digits:
        return

    # remove country code 509 if present
    if digits.startswith('509'):
        local = digits[3:]
    else:
        local = digits

    allowed = getattr(settings, 'PHONE_ALLOWED_PREFIXES', ['34', '35', '36', '37', '38', '39'])
    # check prefix length (2 digits) by default
    if not any(local.startswith(p) for p in allowed):
        raise ValidationError(
            "Le numéro de téléphone doit commencer par un préfixe Digicel ou Natcom valide (ex: %s)."
            % (', '.join(allowed))
        )


def _iter_contact_models():
    """Yield (Model, field_map) for each registered model in CONTACT_FIELD_MAP."""
    for fullpath, fmap in CONTACT_FIELD_MAP.items():
        try:
            app_label, model_name = fullpath.split('.')
            Model = apps.get_model(app_label, model_name)
            if Model:
                yield Model, fmap
        except Exception:
            # if a model isn't available (app not installed) just skip it
            continue


def validate_unique_across_models(field: str, value: str, instance=None):
    """Ensure that `value` for `field` (either 'email' or 'telephone') is unique across configured models.

    Raises ValidationError if a conflict is found.
    `instance` can be provided to exclude the current object (useful on updates).
    """
    if not value:
        return

    # normalize telephone comparison to digits only for telephone
    comp_value = value
    if field == 'telephone':
        comp_value = _normalize_phone(value)

    for Model, fmap in _iter_contact_models():
        model_field = fmap.get(field)
        if not model_field:
            continue

        # Build query dynamically. For telephone, compare normalized digits
        qs = Model.objects.all()

        # Exclude the same instance when updating
        try:
            if instance and hasattr(instance, 'pk') and instance.pk and instance.__class__ == Model:
                qs = qs.exclude(pk=instance.pk)
        except Exception:
            pass

        # For telephone: compare after normalizing stored values if needed
        if field == 'telephone':
            # We compare by normalizing the candidate against stored values.
            # Because stored values may contain formatting chars, we fetch
            # potential candidates by a sensible LIKE filter and then normalize
            # in Python to be certain.
            possible = qs.filter(**{f"{model_field}__isnull": False}).values_list(model_field, 'pk')
            for stored, pk in possible:
                if stored is None:
                    continue
                if _normalize_phone(stored) == comp_value:
                    raise ValidationError(f"Ce numéro de téléphone est déjà utilisé dans le système (par {Model._meta.verbose_name}).")
        else:
            if qs.filter(**{model_field: comp_value}).exists():
                raise ValidationError(f"Cette adresse e-mail est déjà utilisée dans le système (par {Model._meta.verbose_name}).")
