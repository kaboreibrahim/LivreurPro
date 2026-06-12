from django.apps import AppConfig


class DemandeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Demande"

    def ready(self):
        import Demande.signals  # noqa: F401
