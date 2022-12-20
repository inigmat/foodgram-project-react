from django.contrib.auth.models import AbstractUser
from django.db import models


USER_LEVEL_CHOICES = (
    ('admin', 'admin'),
    ('user', 'user'),
)

DEFAULT_USER_LEVEL = 'user'

class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    role = models.CharField(
        max_length=30,
        choices=USER_LEVEL_CHOICES,
        default=DEFAULT_USER_LEVEL,
        verbose_name='Роль'
    )

    @property
    def is_admin(self):
        return self.is_superuser or self.role == "admin"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписка на авторов рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name="unique_following"
            )
        ]
