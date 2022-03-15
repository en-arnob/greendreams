from django.urls import path
from app.views import *

app_name = "app"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("flower-plants/", FlowerPlantsView.as_view(), name='flowers'),
    path("fruit-plants/", FruitPlantsView.as_view(), name="fruits"),
    path("item/<slug:slug>/", DetailsView.as_view(), name="details"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name='addtocart'),
    path("my-cart/", MyCartView.as_view(), name='mycart'),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),

    path("register/", CustomerRegistrationView.as_view(), name='customerreg'),
    path("logout/", CustomerLogoutView.as_view(), name='logout'),
    path("login/", LoginView.as_view(), name='login'),
    path("search/", SearchView.as_view(), name="search"),
    path("about/", AboutView.as_view(), name="about"),
]
