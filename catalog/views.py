import datetime

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.forms import BookInstanceForm, BorrowBookForm, RenewBookForm, StatusUpdateForm, ReturnBookUpdateForm
from .models import Book, Author, BookInstance, Genre, Language


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


# class BookListView(ListView): # LoginRequiredMixin easiest way to require login for class views
#     # login_url = '/login/' # specifies an alt location to redirect if user is not authenticated
#     # redirect_field_name = 'redirect_to' # URL parameter instead of next to insert current abs path
#     model = Book
#     paginate_by = 10
    # Note: How to override standard set variables of the ListView
    # context_object_name = 'book_list' # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location

    # Override class-based methods to change
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    # Pass additional context variables to the template
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

def book_listing(request):
    search_val = request.GET.get("search", False)
    if search_val:
        query = Q(title__icontains=search_val) | (Q(author__first_name__icontains=search_val)) | (Q(author__last_name__icontains=search_val)) | (Q(genre__name__icontains=search_val)) | (Q(language__name__icontains=search_val))
        book_list = Book.objects.filter(query).select_related().distinct().order_by('title')[:10]
    else:
        book_list = Book.objects.all().order_by('title')

    # pagination
    paginator = Paginator(book_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'search': search_val,
        'page_obj': page_obj,
        'is_paginated': True,
    }
    return render(request, 'catalog/book_list.html', context)


class BookDetailView(DetailView):
    model = Book


class AuthorListView(ListView):
    model = Author
    paginate_by = 10

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

            return HttpResponseRedirect(
                reverse('book-detail', kwargs={"pk":book_instance.book.pk})
            )

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = { 'form': form, 'book_instance': book_instance, }

    return render(request, 'catalog/bookinstance_renew_librarian.html', context)


class LoanView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_bookinstance'
    template_name = 'catalog/bookinstance_loan_form.html'

    def get(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = BorrowBookForm(instance=bookinst)
        due_back = datetime.date.today() + datetime.timedelta(weeks=3)
        context = { 'form': form, 'bookinst': bookinst, 'due_back': due_back }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        book = bookinst.book
        form = BorrowBookForm(request.POST, instance=bookinst)

        if not form.is_valid():
            context = { 'form': form, 'bookinst': bookinst }
            return render(request, self.template_name, context)

        book_inst = form.save(commit=False)
        book_inst.status = 'o'
        book_inst.due_back = datetime.date.today() + datetime.timedelta(weeks=3)
        book_inst.save()

        success_url = reverse_lazy('book-detail', kwargs={'pk':book.pk})
        return redirect(success_url)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = [ 'first_name', 'last_name', 'date_of_birth', 'date_of_death' ]
    # initial = { 'date_of_death': '11/11/2023' } # sets initial value for field
    permission_required = 'catalog.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields are added)
    fields = '__all__'
    permission_required = 'catalog.change_author'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    #reverse_lazy() is a lazily executed version of reverse(), used here because
    #we're providing a URL to a class-based view attribute.
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    # we override form_valid to make sure the Author isn't used in any Book
    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_bookinstance'
    template_name = 'catalog/bookinstance_form.html'

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        form = BookInstanceForm()
        context = { 'form': form, 'book': book }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = BookInstanceForm(request.POST)
        book = get_object_or_404(Book, pk=pk)

        if not form.is_valid():
            context = { 'form': form, 'book': book }
            return render(request, self.template_name, context)

        book_inst = form.save(commit=False)
        book_inst.book = book
        book_inst.status = 'm'
        book_inst.save()

        success_url = reverse_lazy('book-detail', kwargs={'pk': pk})
        return redirect(success_url)


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_bookinstance'
    template_name = 'catalog/bookinstance_form.html'

    def get(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = BookInstanceForm(instance=bookinst)
        context = { 'form': form, 'book': bookinst.book }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        book = bookinst.book
        form = BookInstanceForm(request.POST, instance=bookinst)

        if not form.is_valid():
            context = { 'form': form, 'book': book }
            return render(request, self.template_name, context)

        form.save()

        success_url = reverse_lazy('book-detail', kwargs={'pk':book.pk})
        return redirect(success_url)


class BookInstanceStatusUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_bookinstance'
    template_name = 'catalog/bookinstance_status_form.html'

    def get(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = StatusUpdateForm(instance=bookinst)
        context = { 'form': form, 'bookinst': bookinst }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = StatusUpdateForm(request.POST, instance=bookinst)

        if not form.is_valid():
            context = { 'form': form, 'bookinst': bookinst }
            return render(request, self.template_name, context)

        book_inst = form.save(commit=False)
        book_inst.due_back = None
        book_inst.borrower = None
        book_inst.save()

        success_url = reverse_lazy('book-detail', kwargs={'pk':bookinst.book.pk})
        return redirect(success_url)


class BookInstanceReturnUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_bookinstance'
    template_name = 'catalog/bookinstance_return_form.html'

    def get(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = ReturnBookUpdateForm(instance=bookinst)
        context = { 'form': form, 'bookinst': bookinst }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            bookinst = BookInstance.objects.get(id=pk)
        except:
            raise Http404
        form = ReturnBookUpdateForm(request.POST, instance=bookinst)

        if not form.is_valid():
            context = { 'form': form, 'bookinst': bookinst }
            return render(request, self.template_name, context)

        book_inst = form.save(commit=False)
        book_inst.due_back = None
        book_inst.borrower = None
        book_inst.status = 'a'
        book_inst.save()

        success_url = reverse_lazy('book-detail', kwargs={'pk':bookinst.book.pk})
        return redirect(success_url)


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    permission_required = 'catalog.delete_bookinstance'

    def get_success_url(self):
        return reverse('book-detail', kwargs={"pk": self.object.book.pk})


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = [ 'title', 'author', 'summary', 'isbn', 'genre', 'language' ]
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = [ 'title', 'author', 'summary', 'isbn', 'genre', 'language' ]
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalgo.delete_book'

    # make sure that book has not instances
    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )


class GenreListView(PermissionRequiredMixin, ListView):
    model = Genre
    permission_required = 'catalog.change_genre'
    paginate_by = 10


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = [ 'name' ]
    permission_required = 'catalog.add_genre'
    success_url = reverse_lazy('genres')


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = [ 'name' ]
    permission_required = 'catalog.change_genre'
    success_url = reverse_lazy('genres')

# Keep Genre deletion to admin pages


class LanguageListView(PermissionRequiredMixin, ListView):
    model = Language
    permission_required = 'catalog.change_language'
    paginate_by = 10


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = [ 'name' ]
    permission_required = 'catalog.add_language'
    success_url = reverse_lazy('languages')


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = [ 'name' ]
    permission_required = 'catalog.change_language'
    success_url = reverse_lazy('languages')

# Keep Language deletion to admin pages