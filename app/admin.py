from django.contrib import admin
from app.models import *

admin.site.register([Customer, Category, Plant, Cart, CartPlant, Order])
