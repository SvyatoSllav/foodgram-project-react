from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, router
from django.db.models.deletion import Collector
from django.utils.html import format_html

from foodgram_backend import settings

User = get_user_model()


class Recipe(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(
        max_length=200
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='recipe',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(
                    1,
                    message='Время приготовления не может быть меньше 1'
                    )
                    ]
    )
    ingridients = models.ManyToManyField(
        'RecipeIngridients',
        related_name='recipe'
    )
    tag = models.ManyToManyField(
        'Tag',
        related_name='recipe'
    )

    def delete(self, using=None, keep_parents=False):
        if self.pk is None:
            raise ValueError(
                "%s object can't be deleted because its %s attribute is set "
                "to None." % (self._meta.object_name, self._meta.pk.attname)
            )
        using = using or router.db_for_write(self.__class__, instance=self)
        collector = Collector(using=using, origin=self)
        collector.collect([self], keep_parents=keep_parents)
        for ingridient in self.ingridients.all():
            ingridient.delete()
        return collector.delete()

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        ordering = ['-created']


class Ingridient(models.Model):
    name = models.CharField(
        max_length=200
    )
    measurement_unit = models.CharField(
        max_length=200
    )

    def __str__(self) -> str:
        return f'{self.name}'


class RecipeIngridients(models.Model):
    ingridient = models.OneToOneField(
        Ingridient,
        related_name='recipe',
        on_delete=models.CASCADE
    )
    weight = models.IntegerField(
        validators=[MinValueValidator(0.0, message='Значение не может быть меньше 0')],
    )

    def __str__(self) -> str:
        return f'Ingridient: {self.ingridient.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff"
    )

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.color,
            self.name
        )

    def __str__(self) -> str:
        return f'{self.name}'