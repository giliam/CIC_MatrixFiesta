from django.apps import AppConfig

class MatrixConfig(AppConfig):
    name = 'matrix'

    def ready(self):
        # Imports signals handlers
        import matrix.handlers
