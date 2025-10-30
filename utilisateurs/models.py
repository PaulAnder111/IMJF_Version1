from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur Système'),
        ('secretaire', 'Secrétaire'),
        ('directeur', 'Directeur'),
        ('archives', 'Archives'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='archives')
    telephone = models.CharField(max_length=20, blank=True,unique=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def avatar_url(self):
        if self.photo:
            return self.photo.url
        else:
            return None

    @property
    def initial(self):
        return self.first_name[0].upper() if self.first_name else self.username[0].upper()

    # Champs sekirite anplis
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

      

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Fonksyon pratik pou teste wòl yo
    def is_admin(self):
        return self.role == 'admin'

    def is_secretaire(self):
        return self.role == 'secretaire'

    def is_directeur(self):
        return self.role == 'directeur'

    def is_archives(self):
        return self.role == 'archives'

    # Fonksyon pou jere lockout apre echèk login
    def register_failed_login(self):
        self.failed_attempts += 1
        if self.failed_attempts >= 5:  # limit la ka modifyab
            self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save()

    def reset_failed_logins(self):
        self.failed_attempts = 0
        self.locked_until = None
        self.save()

    def is_locked(self):
        return self.locked_until and self.locked_until > timezone.now()


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


# ✅ Création de l'administrateur par défaut (admin sys)
@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
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
            print("Administrateur par défaut créé: Fedanoir / @@fedanoir@@joseph@@2025@@!")
