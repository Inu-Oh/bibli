from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # access appropriate view function by calling the class method as_view()
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailViews.as_view(), name='book-detail'),
]