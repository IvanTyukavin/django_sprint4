from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def handler404(request, exception=None):
    """Кастомная страница ошибки 404 (Страница не найдена)"""
    context = {
        'exception': str(exception) if exception else None
    }
    return render(request, 'pages/404.html', context, status=404)


def handler500(request):
    """Кастомная страница ошибки 500 (Ошибка сервера)"""
    return render(request, 'pages/500.html', status=500)
