# annee_scolaire/admin.py
from django.contrib import admin
from django.contrib import messages
from .models import AnneeScolaire

@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_debut', 'date_fin', 'est_annee_courante', 'est_active', 'est_terminee', 'est_en_cours']
    list_filter = ['est_annee_courante', 'est_active', 'date_debut', 'date_fin']
    search_fields = ['nom']
    
    # AJOUTE CETTE LIGNE :
    actions = ['definir_comme_annee_courante']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'date_debut', 'date_fin')
        }),
        ('Statut', {
            'fields': ('est_annee_courante', 'est_active')
        }),
    )
    
    # AJOUTE CETTE METHODE :
    def definir_comme_annee_courante(self, request, queryset):
        """Définit l'année sélectionnée comme année courante"""
        if queryset.count() != 1:
            self.message_user(
                request, 
                "Sélectionnez exactement UNE année.", 
                level=messages.ERROR
            )
            return
        
        # Désactive TOUTES les années
        AnneeScolaire.objects.update(est_annee_courante=False, est_active=False)
        
        # Active la sélection
        annee = queryset.first()
        annee.est_annee_courante = True
        annee.est_active = True
        annee.save()
        
        self.message_user(
            request, 
            f"✅ {annee.nom} est maintenant l'année courante et active!"
        )
    
    definir_comme_annee_courante.short_description = "Définir comme année courante"
    
    def est_terminee(self, obj):
        return obj.est_terminee
    est_terminee.boolean = True
    est_terminee.short_description = 'Terminée'
    
    def est_en_cours(self, obj):
        return obj.est_en_cours
    est_en_cours.boolean = True
    est_en_cours.short_description = 'En cours'