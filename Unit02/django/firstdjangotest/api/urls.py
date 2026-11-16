from django.contrib import admin
from django.urls import path, include
from .views import get_books, create_book, book_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', get_books, name='get_books'),
    path('books/create/', create_book, name='create_book'),
    path('books/<int:pk>', book_detail, name='book_detail')
]
