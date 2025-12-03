from django.apps import AppConfig


class ApponichanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appOnichan'

    def ready(self):
        import appOnichan.signals
