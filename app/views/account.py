
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from app.models import UserProfile


class AccountCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/create.html"

    def get_success_url(self):
        return reverse("index_view")


class AccountActivateView(TemplateView):
    model = UserProfile
    template_name = "app/userprofile_form.html"
