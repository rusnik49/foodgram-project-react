from api.models import Ingredient, Recipe
from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по их названию"""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        """Метод возвращает QuerySet с заданным именем ингредиента."""
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору/тегу/подписке/наличию в списке покупок"""
    tags = filters.AllValuesMultipleFilter(field_name='tag__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
