from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from eleves.models import Eleve
from enseignants.models import Enseignant
from classes.models import Classe
from matieres.models import Matiere
from inscriptions.models import Inscription
from cours.models import Cours

from .models import HistoriqueAction

User = get_user_model()
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import HistoriqueAction


# --- Connexion ---
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    HistoriqueAction.objects.create(
        user=user,
        action="connexion",
        model_name="Authentification",
        object_id=user.id,
        description=f"L'utilisateur {user.username} s'est connecté."
    )


# --- Déconnexion ---
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    HistoriqueAction.objects.create(
        user=user,
        action="deconnexion",
        model_name="Authentification",
        object_id=user.id,
        description=f"L'utilisateur {user.username} s'est déconnecté."
    )



# ------------ FUNCTION UTILE --------------
def log_action(model_name, instance, action, description):
    HistoriqueAction.objects.create(
        model_name=model_name,
        object_id=instance.id,
        action=action,
        user=None,  # Ou ka mete request.user nan views si vle
        description=description
    )


# ------------ ELEVE ------------
@receiver(post_save, sender=Eleve)
def log_eleve_save(sender, instance, created, **kwargs):
    if created:
        log_action("Eleve", instance, "Création",
                   f"Élève {instance.nom} {instance.prenom} ajouté")
    else:
        log_action("Eleve", instance, "Modification",
                   f"Élève {instance.nom} {instance.prenom} modifié")


@receiver(post_delete, sender=Eleve)
def log_eleve_delete(sender, instance, **kwargs):
    log_action("Eleve", instance, "Suppression",
               f"Élève {instance.nom} {instance.prenom} supprimé")


# ------------ ENSEIGNANT ------------
@receiver(post_save, sender=Enseignant)
def log_enseignant_save(sender, instance, created, **kwargs):
    if created:
        log_action("Enseignant", instance, "Création",
                   f"Enseignant {instance.nom} {instance.prenom} ajouté")
    else:
        log_action("Enseignant", instance, "Modification",
                   f"Enseignant {instance.nom} {instance.prenom} modifié")


@receiver(post_delete, sender=Enseignant)
def log_enseignant_delete(sender, instance, **kwargs):
    log_action("Enseignant", instance, "Suppression",
               f"Enseignant {instance.nom} {instance.prenom} supprimé")


# ------------ CLASSE ------------
@receiver(post_save, sender=Classe)
def log_classe_save(sender, instance, created, **kwargs):
    if created:
        log_action("Classe", instance, "Création",
                   f"Classe {instance.nom} ajoutée")
    else:
        log_action("Classe", instance, "Modification",
                   f"Classe {instance.nom} modifiée")


@receiver(post_delete, sender=Classe)
def log_classe_delete(sender, instance, **kwargs):
    log_action("Classe", instance, "Suppression",
               f"Classe {instance.nom} supprimée")


# ------------ MATIERE ------------
@receiver(post_save, sender=Matiere)
def log_matiere_save(sender, instance, created, **kwargs):
    if created:
        log_action("Matiere", instance, "Création",
                   f"Matière {instance.nom} ajoutée")
    else:
        log_action("Matiere", instance, "Modification",
                   f"Matière {instance.nom} modifiée")


@receiver(post_delete, sender=Matiere)
def log_matiere_delete(sender, instance, **kwargs):
    log_action("Matiere", instance, "Suppression",
               f"Matière {instance.nom} supprimée")


# ------------ INSCRIPTION ------------
@receiver(post_save, sender=Inscription)
def log_inscription_save(sender, instance, created, **kwargs):
    if created:
        log_action("Inscription", instance, "Création",
                   f"Nouvelle inscription pour {instance.eleve}")
    else:
        log_action("Inscription", instance, "Modification",
                   f"Inscription modifiée pour {instance.eleve}")


@receiver(post_delete, sender=Inscription)
def log_inscription_delete(sender, instance, **kwargs):
    log_action("Inscription", instance, "Suppression",
               f"Inscription supprimée pour {instance.eleve}")


# ------------ COURS ------------
@receiver(post_save, sender=Cours)
def log_cours_save(sender, instance, created, **kwargs):
    if created:
        log_action("Cours", instance, "Création",
                   f"Cours {instance.matiere} ajouté")
    else:
        log_action("Cours", instance, "Modification",
                   f"Cours {instance.matiere} modifié")


@receiver(post_delete, sender=Cours)
def log_cours_delete(sender, instance, **kwargs):
    log_action("Cours", instance, "Suppression",
               f"Cours {instance.matiere} supprimé")


# ------------ UTILISATEURS / USER ------------
@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        log_action("Utilisateur", instance, "Création",
                   f"Utilisateur {instance.username} créé")
    else:
        log_action("Utilisateur", instance, "Modification",
                   f"Utilisateur {instance.username} modifié")


@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    log_action("Utilisateur", instance, "Suppression",
               f"Utilisateur {instance.username} supprimé")
