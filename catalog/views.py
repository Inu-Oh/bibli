from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Book, Author, BookInstance, Genre

# @login_required # Easiest way to require login for functions
def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()
    num_instances = BookInstance .objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count
    num_authors = Author.objects.count()

    # Assignment 5.2
    num_genres = Genre.objects.all().count()
    # num_the_books = Book.objects.filter(title__icontains='the').count()

    # Count user visits to this view in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits_plus_1 = num_visits + 1
    request.session['num_visits'] = num_visits_plus_1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        # 'num_the_books': num_the_books,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


class BookListView(ListView): # LoginRequiredMixin easiest way to require login for class views
    # login_url = '/login/' # specifies an alt location to redirect if user is not authenticated
    # redirect_field_name = 'redirect_to' # URL parameter instead of next to insert current abs path
    model = Book
    paginate_by = 5
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


class AuthorListView(ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(DetailView):
    model = Author