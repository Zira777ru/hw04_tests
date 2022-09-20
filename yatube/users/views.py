from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreatingForm


class SignUp(CreateView):
    form_class = CreatingForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'
