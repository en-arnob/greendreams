from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView, FormView
from django.contrib.auth import authenticate, login, logout
from app.models import *
from app.forms import CheckoutForm, CustomerRegistrationForm, LoginForm
from django.urls import reverse_lazy
from django.db.models import Q


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plants'] = Plant.objects.all().order_by('-date')
        return context


class FlowerPlantsView(TemplateView):
    template_name = "flowers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plants'] = Plant.objects.all().order_by('-date')
        return context


class FruitPlantsView(TemplateView):
    template_name = "fruits.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plants'] = Plant.objects.all().order_by('-date')
        return context


class DetailsView(TemplateView):
    template_name = "details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        # slug = self.kwargs['slug]
        item = Plant.objects.get(slug=slug)
        context['item'] = item

        return context


class AddToCartView(TemplateView):

    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get plant id from url
        plant_id = self.kwargs['pro_id']
        # get plant
        plant_obj = Plant.objects.get(id=plant_id)
        # check cart exists or not
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_plant_in_cart = cart_obj.cartplant_set.filter(plant=plant_obj)
            # if plant already exists in cart
            if this_plant_in_cart.exists():
                cartplant = this_plant_in_cart.last()
                cartplant.quantity += 1
                cartplant.subtotal += plant_obj.price
                cartplant.save()
                cart_obj.total += plant_obj.price
                cart_obj.save()
            # if new item is added to cart
            else:
                cartplant = CartPlant.objects.create(
                    cart=cart_obj, plant=plant_obj, rate=plant_obj.price, quantity=1, subtotal=plant_obj.price)
                cart_obj.total += plant_obj.price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartplant = CartPlant.objects.create(
                cart=cart_obj, plant=plant_obj, rate=plant_obj.price, quantity=1, subtotal=plant_obj.price)
            cart_obj.total += plant_obj.price
            cart_obj.save()

        # check if product already exists in cart

        return context


class MyCartView(TemplateView):
    template_name = 'mycart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            context['cart'] = cart
        else:
            cart = None
            context['cart'] = cart

        return context


class ManageCartView(View):

    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartPlant.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        else:
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        return redirect('app:mycart')


class CheckoutView(CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy("app:home")

    def dispatch(self, request, *args, **kwargs):  # login required
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj

        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Recieved"
            del self.request.session['cart_id']
        else:
            return redirect('app:home')

        return super().form_valid(form)


class CustomerRegistrationView(CreateView):
    template_name = 'customerreg.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)  # login immediately after reg
        return super().form_valid(form)

    def get_success_url(self):  # success url for login redirect to cart
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('app:home')


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data.get("password")
        usr = authenticate(username=uname, password=pword)
        if usr is not None and usr.customer:
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid Credentials"})

        return super().form_valid(form)

    def get_success_url(self):  # success url for login redirect to cart
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Plant.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw))
        context['results'] = results

        return context


class AboutView(TemplateView):
    template_name = "about.html"
