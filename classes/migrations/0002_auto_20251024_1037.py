# classes/migrations/0002_populate_classes.py
from django.db import migrations

def create_classes(apps, schema_editor):
    Classe = apps.get_model('classes', 'Classe')
    classes_data = [
        {'nom_classe': '7ème A', 'niveau': '7ème', 'capacite_max': 50, 'code_classe': '001'},
         {'nom_classe': '8ème A', 'niveau': '8ème', 'capacite_max': 50,'code_classe': '002'},
          {'nom_classe': '9ème A', 'niveau': '9ème', 'capacite_max': 50,'code_classe': '003'},
         {'nom_classe': 'NSI A', 'niveau': 'NSI', 'capacite_max': 50,'code_classe': '004'},
        {'nom_classe': 'NSII A', 'niveau': 'NSII', 'capacite_max': 50,'code_classe': '005'},
        {'nom_classe': 'NSIII A', 'niveau': 'NSIII', 'capacite_max': 50,'code_classe': '006'},
         {'nom_classe': 'NSIV A', 'niveau': 'NSIV', 'capacite_max': 50,'code_classe': '007'},
       ]
    
    for data in classes_data:
        Classe.objects.get_or_create(
            nom_classe=data['nom_classe'],
            defaults={
                'niveau': data['niveau'],
                'capacite_max': data['capacite_max'],
                'code_classe': data['code_classe'],
                'statut': 'actif'
            }
        )

def reverse_create_classes(apps, schema_editor):
    Classe = apps.get_model('classes', 'Classe')
    Classe.objects.filter(niveau__in=['7ème', '8ème', '9ème', 'NSI', 'NSII', 'NSIII', 'NSIV']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('classes', '0001_initial'),  # chanje sa si non modèl la diferan
    ]

    operations = [
        migrations.RunPython(create_classes, reverse_create_classes),
    ]