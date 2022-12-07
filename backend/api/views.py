import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CreateListDestroytViewSet
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (FavoritedSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeListSerializer,
                             SubscriptionListSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSerializer)
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """Представление пользователями и подписками на авторов."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, pk=None):
        authors = User.objects.filter(following__user=request.user)
        recipes_limit = request.query_params.get('recipes_limit')
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionListSerializer(
            result_page, many=True, context={
                'current_user': request.user,
                'recipes_limit': recipes_limit
            }
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get', 'delete'],
            permission_classes=[IsAuthenticated], pagination_class=None)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionListSerializer(
            data={'user': request.user, 'author': author},
            context={'request': request}
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=request.user)
            serializer = SubscriptionSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(Subscription, author=author,
                                         user=request.user)
        self.perform_destroy(subscription)
        return Response(
            f'{request.user} отписан от {author}',
            status=status.HTTP_204_NO_CONTENT
        )


class TagsViewSet(CreateListDestroytViewSet):
    """Тэги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(CreateListDestroytViewSet):
    """Ингридиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        response_errors = {
            'POST': 'Вы уже добавили этот рецепт в избранное',
            'DELETE': 'Вы еще не добавили этот рецепт в избранное',
        }
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST' and not in_favorite:
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoritedSerializer(favorite.recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE' and in_favorite:
            in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        response = {'errors': response_errors[request.method]}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        response_errors = {
            'POST': 'Рецепт уже добавлен в списко покупок',
            'DELETE': 'Рецепт в корзине отсутствует',
        }
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if request.method == 'POST' and not in_shopping_cart:
            shopping_cart = ShoppingCart.objects.create(user=user,
                                                        recipe=recipe)
            serializer = FavoritedSerializer(shopping_cart.recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE' and in_shopping_cart:
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        response = {'errors': response_errors[request.method]}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientsRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'ingredient_amount')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Shoppingcart.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response