from django.apps import AppConfig


class CoreConfig(AppConfig):
    # Correction : l'app s'appelait "myproject" (le nom du PROJET). Le lab cree l'app "core"
    # avec "python manage.py startapp core" : le projet = l'ecole, l'app = un departement.
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
