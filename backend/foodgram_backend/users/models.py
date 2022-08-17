from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from foodgram_backend import settings


class User(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        unique=True,
        help_text='Ваше имя',
        validators=[UnicodeUsernameValidator, ],
        error_messages={'unique': 'Ваше имя не уникально'}
    )
    email = models.EmailField(
        'email address',
        max_length=254,
        blank=False,
    )
    first_name = models.CharField(
        'first_name',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'last_name',
        max_length=150,
        blank=False
    )
    wish_list = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name=('wish_list'),
        related_name='user_wishlist',
        blank=True
    )
    shop_list = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name=('shop_list'),
        related_name='user_shoplist',
        blank=True
    )

    def clean(self) -> None:
        if self.username == 'me':
            raise ValidationError('Ваше имя не может быть "me".')

    def __str__(self) -> str:
        return f'{self.username}'


class Follow(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_followers'
            )
        ]

        ordering = ['-created']

    def clean(self) -> None:
        if self.follower == self.following:
            raise ValidationError('Вы не можете подписываться на себя')

    def __str__(self) -> str:
        return f'{self.follower} follows {self.following}'
