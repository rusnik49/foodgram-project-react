from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        null=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX код',
        max_length=7,
        unique=True,
        null=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов',
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте',
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite',
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shoppingcart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shoppingcart',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-id',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_follow',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
