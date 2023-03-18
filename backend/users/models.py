from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='Эл.почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
