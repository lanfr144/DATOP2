from datetime import date

from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Les 2 roles d'un serializer : convertir Book <-> JSON, et valider les donnees entrantes."""

    class Meta:
        model = Book
        fields = "__all__"

    # Exercice 3 "Your turn" 1 : DRF appelle automatiquement validate_<champ>
    def validate_published(self, value):
        if value > date.today():
            raise serializers.ValidationError("The publication date cannot be in the future.")
        return value
