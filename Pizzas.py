from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from pytz import country_names
from rest_framework.viewsets import ModelViewSet


class VegToppingChoices:
    MEAT = 1
    VEG = 2
    VEGAN = 3

    CHOICES = (
        (MEAT, 'MEAT'),
        (VEG, 'VEG'),
        (VEGAN, 'VEGAN')
    )


class PizzaSizesChoices:
    XL = 1
    L = 2
    M = 3

    CHOICES = (
        (XL, 'XL'),
        (L, 'L'),
        (M, 'M')
    )


class GeoLocation(models.Model):
    latitude = models.DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)
    street = models.CharField(max_length=400, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=2, choices=country_names.items(), blank=True, null=True)

    def __str__(self):
        return f'{self.street}, {self.city}, {self.country}'


class DefaultUser(AbstractUser):
    email = models.EmailField()
    address = models.OneToOneField(GeoLocation, models.PROTECT)


class Topping(models.Model):
    """
    This won't be a choices field on Pizza, because every topping has it's own attributes,
    price, veggie...
    """
    name = models.CharField(max_length=255)
    price = models.DecimalField()
    veggie = models.IntegerField(VegToppingChoices.CHOICES)


class Pizza(models.Model):
    """
    Now youll have to create DB row for pizza with olives, pizza with bacon, pizza with olives and bacon,
    EVERY FUCKING TIME,
    and most of all, in order to add topping you will have to create a pizza too because they are in the same model!
    """
    name = models.CharField()
    price = models.DecimalField()
    toppings = models.ManyToManyField(Topping, null=True, blank=True, related_name='toppings')
    size = models.IntegerField(PizzaSizesChoices.CHOICES, default=1)
    topping_name = models.CharField(max_length=255)
    topping_price = models.DecimalField()
    veggie = models.IntegerField(VegToppingChoices.CHOICES)


class PizzaWithOutRelation(models.Model):
    name = models.CharField()
    price = models.DecimalField()
    toppings = models.ManyToManyField(Topping, null=True, blank=True, related_name='toppings')
    size = models.IntegerField(PizzaSizesChoices.CHOICES, default=1)


class Order(models.Model):
    pizza = models.ManyToManyField(Pizza, null=False, blank=False, related_name='pizzas')
    user = models.ForeignKey(DefaultUser, on_delete=models.CASCADE, related_name='user_orders')
    ordered_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.ordered_at = timezone.now()
        super(Order, self).save(*args, **kwargs)


class MockView(ModelViewSet):

    def get_queryset(self):
        # ONLY ONE QUERY TO DB TO FETCH ALL DATA, extremely efficient
        query = DefaultUser.objects.filter(email=self.request.user.email).prefetch_related('user_orders',
                                                                                           'user__orders__pizzas',
                                                                                           'user__orders__pizzas__toppings')
        return query

    def get_most_used_user_toppings(self):
        query = self.get_queryset()
        # doesnt go to the DB again
        top_five_toppings = query.user__orders__pizzas__toppings.all()[:5]
        return top_five_toppings
