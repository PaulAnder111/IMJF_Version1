from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate, post_delete
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
# Notification model (simple implementation used by views)
# ==========================================================
class Notification(models.Model):
    NOTIF_TYPES = (
        ('inscription', 'Inscription'),
        ('action_secretaire', 'Action Secrétaire'),
        ('action_archives', 'Action Archives'),
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('systeme', 'Système'),
        ('validation', 'Validation'),
    )

    # user may be null for role-targeted or broadcast notifications
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='notifications', null=True, blank=True)
    type = models.CharField(max_length=50, choices=NOTIF_TYPES, default='systeme')
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_url = models.CharField(max_length=255, null=True, blank=True)
    read = models.BooleanField(default=False)
    # role-based targeting: set recipient_role to a role name (eg. 'admin') to target that role
    recipient_role = models.CharField(max_length=50, null=True, blank=True)
    # broadcast: if True the notification targets everyone (but individual read state tracked via recipients)
    broadcast = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilisateurs_notifications'
        ordering = ['-created_at']

    def __str__(self):
        user_part = self.user.username if self.user else f"role:{self.recipient_role or 'all'}"
        return f"Notification({user_part}) - {self.title}"


# Per-user recipient/read state for notifications. This lets us create shared
# Notification objects targeted to a role or broadcast, while tracking whether
# each specific user has read the notification.
class NotificationRecipient(models.Model):
    notification = models.ForeignKey('Notification', on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notification_recipients')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notification', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Recipient({self.user.username}) for Notification({self.notification.id})"


# ==========================================================
# ✅ USER SESSION TRACKING (Pou monitore koneksyon/dekoneksyon)
# ==========================================================
class UserSession(models.Model):
    """Track user login/logout activity in real-time"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=32, unique=True, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Logged Out"
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')} ({status})"

    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.logout_time or timezone.now()
        return end_time - self.login_time

    @property
    def duration_display(self):
        """Return formatted duration like '2h 30m 45s' or '15m 30s'"""
        duration = self.duration
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        remaining = total_seconds % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    @property
    def login_time_display(self):
        """Return formatted login time"""
        return self.login_time.strftime('%d/%m/%Y %H:%M:%S')
    
    @property
    def logout_time_display(self):
        """Return formatted logout time"""
        if self.logout_time:
            return self.logout_time.strftime('%d/%m/%Y %H:%M:%S')
        return None


# ==========================================================
# ✅ SIGNAL HANDLERS (Track logout)
# ==========================================================
@receiver(post_delete)
def track_session_logout(sender, instance, **kwargs):
    """Mark session as logged out when user logs out"""
    if sender.__name__ == 'Session':
        # When Django session is deleted, mark UserSession as logged out
        try:
            session = UserSession.objects.get(session_key=instance.session_key)
            session.is_active = False
            session.logout_time = timezone.now()
            session.save()
        except UserSession.DoesNotExist:
            pass


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
