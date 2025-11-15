from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HistoriqueAction
from django.http import HttpResponse
import csv

@login_required
def historique_list(request):
    actions = HistoriqueAction.objects.select_related('user').all()

    # --- Filtrage selon GET params ---
    model_filter = request.GET.get('model')
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    search = request.GET.get('search')

    if model_filter and model_filter != 'all':
        actions = actions.filter(model_name=model_filter)

    if user_filter and user_filter != 'all':
        try:
            user_filter_id = int(user_filter)
            actions = actions.filter(user__id=user_filter_id)
        except ValueError:
            pass  # ignore si user='all'

    if action_filter and action_filter != 'all':
        actions = actions.filter(action=action_filter)

    if search:
        actions = actions.filter(description__icontains=search)

    # --- Listes pour dropdown ---
    models_list = HistoriqueAction.objects.values_list('model_name', flat=True).distinct()
    users_list = HistoriqueAction.objects.exclude(user__isnull=True).values_list('user__id', 'user__username').distinct()
    actions_list = HistoriqueAction.ACTION_CHOICES

    context = {
        'actions': actions,
        'models_list': models_list,
        'users_list': users_list,
        'actions_list': actions_list,
        'selected_model': model_filter or 'all',
        'selected_user': int(user_filter) if user_filter and user_filter != 'all' else 'all',
        'selected_action': action_filter or 'all',
        'search': search or ''
    }
    return render(request, 'historique.html', context)



@login_required
def export_csv(request):
    actions = HistoriqueAction.objects.select_related('user').all()

    # --- Récupération des filtres ---
    model_filter = request.GET.get('model')
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    search = request.GET.get('search')

    # --- Application des filtres ---
    if model_filter and model_filter != 'all':
        actions = actions.filter(model_name=model_filter)

    if user_filter and user_filter != 'all':
        try:
            user_id = int(user_filter)
            actions = actions.filter(user__id=user_id)
        except ValueError:
            pass

    if action_filter and action_filter != 'all':
        actions = actions.filter(action=action_filter)

    if search:
        actions = actions.filter(description__icontains=search)

    # --- Création du fichier CSV ---
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historique.csv"'

    writer = csv.writer(response)
    writer.writerow(['Utilisateur', 'Action', 'Modèle', 'ID Objet', 'Description', 'Date'])

    for a in actions:
        utilisateur = a.user.username if a.user else "System"
        writer.writerow([utilisateur, a.get_action_display(), a.model_name, a.object_id, a.description, a.date_action])

    return response
