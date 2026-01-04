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