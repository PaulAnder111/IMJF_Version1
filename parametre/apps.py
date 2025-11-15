from django.apps import AppConfig


class ParametreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parametre'

    def ready(self):
        import parametre.signals  # Asire w ke siyal yo enpòte lè app a pare