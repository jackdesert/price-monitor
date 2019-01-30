# It appears you can also use shortcuts:


from django.shortcuts import render
from simpletire.models import StatsPresenter
from simpletire.models import Catalog
import ipdb

def stats_view(request):
    context = {}
    context['tires'] = StatsPresenter.tire_stats()
    context['base_url'] = Catalog.BASE_URL

    return render(request, 'stats.jinja2', context)







# The hard way that doesn't work because super() fails if no arguments
#
# from django.views.generic.base import TemplateView
# class StatsView(TemplateView):
#
#     template_name = "stats.html"
#
#     def get_context_data(self, **kwargs):
#         data = dict(hi=5)
#         ipdb.set_trace()
#         # ipdb.set_trace()
#         # context = super().get_context_data(**kwargs)
#         # context['latest_articles'] = Article.objects.all()[:5]
#         return data
