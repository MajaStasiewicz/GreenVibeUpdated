
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django import forms
from django.urls import reverse_lazy
    
class RegisterUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'dataOrder', 'placeholder': 'NAZWA UŻYTKOWNIKA'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'EMAIL'}))
    first_name = forms.CharField(
        max_length=50,
        label="Imię",
        widget=forms.TextInput(attrs={'class': 'dataOrder', 'placeholder': 'IMIĘ'})
    )
    last_name = forms.CharField(
        max_length=100,
        label="Nazwisko",
        widget=forms.TextInput(attrs={'class': 'dataOrder', 'placeholder': 'NAZWISKO'})
    )
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'dataOrder', 'placeholder': 'HASŁO'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'dataOrder', 'placeholder': 'POTWIERDŹ HASŁO'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

