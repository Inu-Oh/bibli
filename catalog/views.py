import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from catalog.forms import RenewBookForm
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


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
                .filter(status__exact='o')
                .order_by('due_back')
        )


class LoanedBooksAllListView(PermissionRequiredMixin, ListView):
    """Generic class-based view listing all books borrowed from library."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )


from django.contrib.auth.decorators import login_required, permission_required

@login_required # Easiest way to require login for functions
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = { 'form': form, 'book_instance': book_instance, }

    return render(request, 'catalog/book_renew_librarian.html', context)