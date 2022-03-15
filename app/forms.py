from django import forms
from .models import Order, Customer
from django.contrib.auth.models import User


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['ordered_by', 'shipping_address', 'phone', 'email', ]


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ['username', 'password', 'email', 'fullname']
    # username validation

    def clean_username(self):
        uname = self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username is already taken")
        return uname


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
