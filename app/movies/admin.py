from django.contrib import admin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import (
    Genre, Filmwork, GenreFilmwork, PersonFilmwork, Person, RoleType
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('id', 'name')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ('genre',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    ordering = ('full_name',)
    search_fields = ('id', 'full_name',)


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline,)

    list_display = (
        'title', 'type', 'creation_date', 'rating', 'get_genres',
        'get_directors', 'get_actors', 'get_writers',
    )
    list_prefetch_related = ('genres', 'persons')
    list_filter = ('type', 'genres',)
    search_fields = ('title', 'description', 'id', 'persons__full_name',)
    empty_value_display = _('unknown')

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .prefetch_related(*self.list_prefetch_related)
            .annotate(
                film_genres=ArrayAgg('genres__name', distinct=True),
                actors=self.get_role_array(RoleType.ACTOR),
                directors=self.get_role_array(RoleType.DIRECTOR),
                writers=self.get_role_array(RoleType.WRITER)
            )
        )
        return queryset

    def get_genres(self, obj):
        return ', '.join(obj.film_genres)
    get_genres.short_description = _('Film genres')

    def get_role_array(self, role):
        return ArrayAgg(
            'persons__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )

    def get_actors(self, obj):
        return ', '.join(obj.actors)
    get_actors.short_description = _('actors')

    def get_directors(self, obj):
        return ', '.join(obj.directors)
    get_directors.short_description = _('directors')

    def get_writers(self, obj):
        return ', '.join(obj.writers)
    get_writers.short_description = _('writers')
