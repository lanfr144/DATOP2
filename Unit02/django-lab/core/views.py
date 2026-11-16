"""
Vues DRF du lab 02c.

Exercice 1 : hello_world (+ "Your turn" : hello_name, server_time)
Exercice 3 : vues "a la main" book_list_create / book_detail (gardees pour comparaison)
Exercice 4 : vues generiques BookListCreate / BookDetail avec recherche (?search=)
"""
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book
from .serializers import BookSerializer


# ---------- Exercice 1 ----------
# Correction : hello_world manquait alors que core/urls.py l'utilise pour /hello/.
@api_view(["GET"])
def hello_world(request):
    # Un POST sur /hello/ renvoie 405 Method Not Allowed : seul GET est autorise.
    return Response({"message": "Hello, DRF!"})


@api_view(["GET"])
def hello_name(request, name: str):
    return Response({"message": f"Hello, {name}!"})


@api_view(["GET"])
def server_time(request):
    return Response({"time": datetime.now().isoformat(timespec="seconds")})


# ---------- Exercice 3 : vues ecrites a la main ----------
@api_view(["GET", "POST"])
def book_list_create(request):
    if request.method == "GET":
        data = Book.objects.all()
        ser = BookSerializer(data, many=True)   # many=True : une liste d'objets
        return Response(ser.data)
    # POST
    ser = BookSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", "PUT", "DELETE"])
def book_detail(request, pk: int):
    # Exercice 3 "Your turn" 2 : get_object_or_404 remplace le bloc try / except Book.DoesNotExist.
    # Meme comportement : DRF transforme Http404 en reponse 404 {"detail": "No Book matches the given query."}
    book = get_object_or_404(Book, pk=pk)

    if request.method == "GET":
        return Response(BookSerializer(book).data)
    if request.method in ["PUT", "PATCH"]:
        # PATCH = mise a jour partielle (champs manquants autorises)
        ser = BookSerializer(book, data=request.data, partial=(request.method == "PATCH"))
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    book.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Exercice 4 : vues generiques (meme comportement, beaucoup moins de code) ----------
class BookListCreate(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # Correction : ligne mal indentee (IndentationError) dans la version precedente
    # Exercice 4 + "Your turn" : recherche (?search=) ET tri (?ordering=-published)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author"]        # champs recherches (icontains)
    ordering_fields = ["published", "title"]   # champs autorises pour ?ordering=


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
