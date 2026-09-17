from django.apps import AppConfig


class BloodbankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bloodbank'
    verbose_name = 'Blood Donate & Request'

    def ready(self):
        import bloodbank.signals  # noqa: F401
