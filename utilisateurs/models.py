from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur Système'),
        ('secretaire', 'Secrétaire'),
        ('directeur', 'Directeur'),
        ('enseignant', 'Enseignant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='enseignant')
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'utilisateurs'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin'
    
    def secretaire(self):
        return self.role == 'secretaire'
    
    def directeur(self):
        return self.role == 'directeur'
    
    def is_teacher(self):
        return self.role == 'enseignant'

# Création de l'administrateur par défaut
@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == 'utilisateurs':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(role='admin').exists():
            User.objects.create_superuser(
                username='IMJFSysAdmin',
                email='admin@ecole.com',
                password='Trilogic2025@!',
                role='admin',
                
            )
            print("Administrateur par défaut créé: IMJFSysAdmin / Trilogic2025@!")