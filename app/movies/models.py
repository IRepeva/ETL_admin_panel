import uuid
from enum import Enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        db_table = "content\".\"genre"
        indexes = [
            models.Index("name", name="genre_name_idx"),
        ]
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_('film'),
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_('genre')
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        indexes = [
            models.Index("genre", name="genre_id_idx"),
        ]
        verbose_name = _('film genre')
        verbose_name_plural = _('film genres')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full_name'))

    class Meta:
        db_table = "content\".\"person"
        indexes = [
            models.Index("full_name", name="person_full_name_idx"),
        ]
        verbose_name = _('participant')
        verbose_name_plural = _('participants')

    def __str__(self):
        return self.full_name


class RoleType(models.TextChoices, Enum):
    ACTOR = 'actor', _('actor')
    PRODUCER = 'producer', _('producer')
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        'Filmwork',
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_('film')
    )
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        db_index=False,
        verbose_name=_('person')
    )
    role = models.TextField(
        _('role'),
        max_length=255,
        choices=RoleType.choices,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            models.Index("person", name="person_id_idx"),
        ]
        verbose_name = _('participant')
        verbose_name_plural = _('participants')


class FilmType(models.TextChoices, Enum):
    MOVIE = 'movie', _('movie')
    TV_SHOW = 'tv_show', _('TV show')


class Filmwork(TimeStampedMixin, UUIDMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(
        _('rating'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = models.CharField(
        _('type'),
        max_length=255,
        choices=FilmType.choices,
    )
    certificate = models.CharField(
        _('certificate'), blank=True, null=True, max_length=512
    )
    file_path = models.FileField(
        _('file'), blank=True, null=True, upload_to='movies/'
    )

    genres = models.ManyToManyField(
        Genre, through='GenreFilmwork', verbose_name=_('genres')
    )
    persons = models.ManyToManyField(
        Person, through='PersonFilmwork', verbose_name=_('participants')
    )

    class Meta:
        db_table = "content\".\"film_work"
        indexes = [
            models.Index("title", name="film_work_title_idx"),
            models.Index("creation_date", name="film_work_creation_date_idx"),
            models.Index("modified", name="film_work_modified_idx"),
        ]
        verbose_name = _('movie')
        verbose_name_plural = _('movies')

    def __str__(self):
        return self.title
