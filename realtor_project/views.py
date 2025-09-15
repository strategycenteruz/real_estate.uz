from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "home.html"

class FormView(TemplateView):
    template_name = "form.html"