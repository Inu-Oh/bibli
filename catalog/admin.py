from django.contrib import admin

from .models import Author, Book, BookInstance, Genre, Language


class AuthorAdmin(admin.ModelAdmin):
    # Controls display of the admin list view
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # Controls dispaly of the admin detail form. Tuple puts items on one line.
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # exclude = ['id'] # will create a form with all fields but id


admin.site.register(Author, AuthorAdmin)


# admin.site.register(Book)
# admin.site.register(BookInstance)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )


admin.site.register(Genre)
admin.site.register(Language)