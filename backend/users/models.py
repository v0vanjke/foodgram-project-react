from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend import constants


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Логин',
        max_length=constants.MAX_USERNAME_LENGHT,
        unique=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=constants.MAX_USER_PASSWORD_LENGHT,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=constants.MAX_USER_FIRST_NAME_LENGHT,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=constants.MAX_USER_LAST_NAME_LENGHT,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=constants.ROLES,
        default=constants.USER_ROLE,
        blank=True,
        max_length=100,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.constants.ADMIN_ROLE or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.constants.USER_ROLE


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_together'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')), name='author_isnt_user'
            ),
        ]
