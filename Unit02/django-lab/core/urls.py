# Correction : fichier manquant (ModuleNotFoundError: No module named 'core.urls').
from django.urls import path

from .views import (BookDetail, BookListCreate, book_detail, book_list_create, hello_name,
                    hello_world, server_time)

urlpatterns = [
    path("hello/", hello_world, name="hello"),
    path("hello/<str:name>/", hello_name, name="hello-name"),
    path("time/", server_time, name="time"),
    # Exercice 4 : vues generiques. Les vues de l'exercice 3 restent accessibles sous /v1/ pour comparer.
    path("books/", BookListCreate.as_view(), name="book-list-create"),
    path("books/<int:pk>/", BookDetail.as_view(), name="book-detail"),
    path("v1/books/", book_list_create, name="v1-book-list-create"),
    path("v1/books/<int:pk>/", book_detail, name="v1-book-detail"),
]
