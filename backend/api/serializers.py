from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import User, Subscription


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с таким именем!'
            )
        return value


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""

    is_subscribed = SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=object.id
        ).exists()


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Отображение краткой информации о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для добавления/удаления подписки и просмотра подписок."""

    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count'))

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return RecipeInfoSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного описания ингредиентов в рецептах."""
    name = serializers.CharField(
        source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта.
    Валидирует ингредиенты."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        list_ingr = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, distinct_ingredients = (
            len(list_ingr), len(set(list_ingr)))

        if all_ingredients != distinct_ingredients:
            raise ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        return data

    def get_ingredients(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        tag = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user,
                                       **validated_data)
        recipe.tag.set(tag)
        self.get_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tag = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredients')

        IngredientInRecipe.objects.filter(recipe=instance).delete()

        instance.tag.set(tag)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""
    tag = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(read_only=True, many=True,
                                               source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shoppingcart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tag', 'author', 'ingredients',
                  'is_favorited', 'is_in_shoppingcart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    def get_is_in_shoppingcart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcart.filter(recipe=object).exists


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/удаления рецепта в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeInfoSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор  для добавления/удаления рецепта в список покупок."""
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
