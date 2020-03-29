from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render

from .forms import CustomUserCreationForm

# Create your views here.

class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    
