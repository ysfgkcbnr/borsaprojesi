# apps.py
from django.apps import AppConfig

class BorsaConfig(AppConfig):
    name = 'borsa'

    def ready(self):
        import borsa.signals  # signals.py dosyasını içe aktar
