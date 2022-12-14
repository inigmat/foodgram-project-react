from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User

MIN_COOKING_TIME = 1
MIN_INGREDIENTS_AMOUNT = 1


class Tag(models.Model):
    """Модель тэгов к рецептам."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True
    )
    color = ColorField(
        default='#FF0000',
        unique=True,
        max_length=7,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Некорректный slug',
                code='invalid_slug',
            ),
        ])

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name='Единица измерения',
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепта."""
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredients',
        verbose_name='Список ингредиентов',
        through='IngredientsRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        verbose_name='Изображение блюда',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Напишите время приготовления в минутах',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                'Минимальное время приготовления - 1 минута.'
            ),
        ]
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    """Количество ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(
            MIN_INGREDIENTS_AMOUNT,
            'Количество элементов должно быть больше 0'),
        )
    )

    class Meta:
        unique_together = ('ingredients', 'amount')
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredients} - {self.amount}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """Рецепты, добавленные для покупки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'
