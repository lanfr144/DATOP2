from django.db import models


class Book(models.Model):
    """Une classe = une table (core_book). Creer la table : makemigrations + migrate."""
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.author})"
