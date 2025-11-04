from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from core.models import BaseModel  # Pou email & téléphone inik

# ==========================================================
# ✅ VALIDATÈ POU IMAJ ITILIZATÈ A
# ==========================================================
def validate_image(fieldfile_obj):
    """Valide foto itilizatè a (taille + extension)."""
    filesize = fieldfile_obj.file.size
    megabyte_limit = 3.0  # limit 3 Mo
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"La taille maximale de l’image est {megabyte_limit} Mo.")

    valid_extensions = ['jpg', 'jpeg', 'png']
    ext = fieldfile_obj.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Format d’image non autorisé (seulement jpg, jpeg, png).")


# ==========================================================
# ✅ MODÈL ITILIZATÈ PÈSONALIZE (CustomUser)
# ==========================================================
class CustomUser(AbstractUser, BaseModel):
    """
    Modèl itilizatè prensipal la.
    Hérite de AbstractUser + BaseModel (pou imel & telefòn inik).
    """

    ROLE_CHOICES = (
        ('admin', 'Administrateur Système'),
        ('secretaire', 'Secrétaire'),
        ('directeur', 'Directeur'),
        ('archives', 'Archives'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='archives')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    photo = models.ImageField(
        upload_to='utilisateurs/photos/',
        validators=[validate_image],
        blank=True,
        null=True,
        default='utilisateurs/photos/default_avatar.png',
        verbose_name="Photo de profil"
    )

    # Champs sekirite
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # ✅ Fonksyon pou wòl itilizatè yo
    def is_admin(self): return self.role == 'admin'
    def is_secretaire(self): return self.role == 'secretaire'
    def is_directeur(self): return self.role == 'directeur'
    def is_archives(self): return self.role == 'archives'

    # ✅ Fonksyon sekirite kont brute-force
    def register_failed_login(self):
        """Anrejistre echèk login pou itilizatè a."""
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save()

    def reset_failed_logins(self):
        """Reyinisyalize kont apre koneksyon siksè."""
        self.failed_attempts = 0
        self.locked_until = None
        self.save()

    def is_locked(self):
        """Verifye si kont itilizatè a bloke."""
        return self.locked_until and self.locked_until > timezone.now()

    # ✅ Fonksyon pou entèfas (UI)
    @property
    def avatar_url(self):
        return self.photo.url if self.photo else '/static/img/default_avatar.png'

    @property
    def initial(self):
        """Retounen premye lèt non itilizatè a (pou inisyal avatar)."""
        return (self.first_name[0] if self.first_name else self.username[0]).upper()


# ==========================================================
# ✅ AUDIT LOG (Pou swiv aksyon itilizatè yo)
# ==========================================================
class AuditLog(models.Model):
    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=255, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} | {self.actor} | {self.action}"
# ==========================================================
# ✅ KÒD RESET MODPAS (
# ==========================================================

class PasswordResetCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"Code reset for {self.user.username} - {self.code}"



# ==========================================================
# ✅ ADMIN DEFAULT (Pou premye koneksyon)
# ==========================================================
@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """Kreye yon administratè default apre migrasyon si pa gen okenn."""
    if sender.name == 'utilisateurs':
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not User.objects.filter(role='admin').exists():
            User.objects.create_superuser(
                username='Fedanoir',
                email='institutionmixtejosephfedanoir@gmail.com',
                password='@@fedanoir@@joseph@@2025@@!',
                role='admin',
            )
            print("✅ Administrateur par défaut créé: Fedanoir / @@fedanoir@@joseph@@2025@@!")
