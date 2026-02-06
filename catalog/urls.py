from django.urls import path
from . import views

urlpatterns = [
    # Browsing
    path('', views.index, name='index'),
    # access appropriate view function by calling the class method as_view()
    path('books/', views.book_listing, name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

    # User views
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),

    # Librarian views
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('bookinst/<uuid:pk>/loan/', views.LoanView.as_view(), name='loan-book'),
    path('bookinst/<uuid:pk>/change_status/',
        views.BookInstanceStatusUpdate.as_view(), name='status-update'),

    # Author CRUD
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    # Book CRUD
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),

    # Book Instance CRUD
    path('book/<int:pk>/bookinst/create/', views.BookInstanceCreate.as_view(), name='bookinst-create'),
    path('bookinst/<uuid:pk>/update/', views.BookInstanceUpdate.as_view(), name='bookinst-update'),
    path('bookinst/<uuid:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinst-delete'),

    # Genre CRUD - no delete page except on admin site
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),

    # Language: CRUD - no delete page except on admin site
    path('language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('language/<int:pk>/update/', views.LanguageUpdate.as_view(), name='language-update'),
]