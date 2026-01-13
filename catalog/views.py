from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()
    num_instances = BookInstance .objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count
    num_authors = Author.objects.count()

    # Assignment 5.2
    num_genres = Genre.objects.all().count()
    # num_the_books = Book.objects.filter(title__icontains='the').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        # 'num_the_books': num_the_books,
    }

    return render(request, 'index.html', context=context)


class BookListView(ListView):
    model = Book

    # Note: How to override standard set variables of the ListView
    # context_object_name = 'book_list' # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location

    # Override class-based methods to change
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    # Pass aaddition context context variables to the template
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context


class BookDetailView(DetailView):
    model = Book