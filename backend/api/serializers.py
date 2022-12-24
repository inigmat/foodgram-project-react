import re

from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User

MIN_AMOUNT_ERR_MSG = "Значение должно быть больше 0"
MIN_QTY_ERR_MSG = 'Укажите минимум 1 ингридиент'


class SignUpSerializer(UserCreateSerializer):
    """Регистрация пользователей."""
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Данный email уже используется')
        return value

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя "me" не допустимо'
            )
        reg = re.compile(r'^[\w.@+-]+$')
        if not reg.match(value):
            raise serializers.ValidationError(
                'Для имени допустимы буквы, цифры and и знаки @.+-_'
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Данное имя уже используется'
            )
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(UserSerializer):
    """Данные зарегистрированных пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, value):
        user = self.context['request'].user
        if user.is_authenticated:
            subscription = Subscription.objects.filter(author=value, user=user)
            return subscription.exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Тэги рецепетов."""
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавить рецепт в избранное."""
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user__id=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                {'ошибка': 'Нельзя добавить повторно рецепт в избранное.'}
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class ShoppingSerializer(FavoriteSerializer):
    """Добавить рецепт в список покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if ShoppingCart.objects.filter(
            user__id=user, recipe__id=recipe
        ).exists():
            raise serializers.ValidationError(
                {'ошибка': 'Этот рецепт уже есть в вашем списке покупок.'}
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class FavoritedSerializer(serializers.ModelSerializer):
    """Получение избранных рецептов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class IngredientSerializer(serializers.ModelSerializer):
    """Список ингридиентов."""
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Класс количества ингредиентов."""
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipe
        fields = [
            'id',
            'amount'
        ]


class RecipeListSerializer(serializers.ModelSerializer):
    """Получение рецепта."""
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(
            cart__user=user,
            id=obj.id
        ).exists()

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient__amount'))


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(many=True,)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('author', 'ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if ingredients == []:
            raise serializers.ValidationError(MIN_QTY_ERR_MSG)
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(MIN_AMOUNT_ERR_MSG)
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            IngredientsRecipe.objects.get_or_create(
                recipe=recipe,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientsRecipe.objects.filter(recipe=instance).all().delete()
        for ingredient in validated_data.get('ingredients'):
            ingredient_amount_obj = IngredientsRecipe.objects.create(
                recipe=instance,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredient_amount_obj.save()
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context=self.context
        )
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Возвращает пользователей, на которых подписан текущий пользователь.
       В выдачу добавляются рецепты."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, value):
        queryset = Recipe.objects.filter(author=value)
        if not self.context.get('recipes_limit'):
            recipes = queryset
        else:
            recipes = queryset[:int(self.context['recipes_limit'])]
        return FavoritedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()
