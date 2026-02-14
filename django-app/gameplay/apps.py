from django.apps import AppConfig


class GameplayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gameplay'
    
    def ready(self):
        # Import signals to auto-create UserProfile
        import gameplay.signals
