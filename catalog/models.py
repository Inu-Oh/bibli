from django.db import models
from django.urls import reverse


class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(
        max_length = 200,
        unique=True,
        help_text="Enter a book genre (e.g.Sci-Fi, Manga etc)"
    )

    def __str__(self):
        """String for representing the genre instance."""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower('name'),
                name = 'genre_name_case_insensitive_unique',
                violation_error_message = "Genre already exists (case insenstive match)"
            ),
        ]


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)

    # Author as a string rather than object because it hasn't been declared yet in file.
    # models.RESTRICT prevents author being deleted if it is referenced by any book.
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, unique=True,
        help_text='13 character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # Genre class has already been defined so we can specify the object.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    def __str__(self):
        """String for representing the book instance."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for a book instance."""
        return reverse('book-detail', args=[str(self.id)])
