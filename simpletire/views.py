# It appears you can also use shortcuts:


from django.shortcuts import render
from django.shortcuts import redirect
from simpletire.models import Catalog
from simpletire.models import StatsPresenter
from simpletire.models import Tire
from simpletire.models import Util
import ipdb

def stats_view(request):
    dimensions = {}
    for dimension in Tire.DIMENSIONS:
        value = request.GET.get(dimension)
        if value:
            dimensions[dimension] = int(value)

    if not Tire.valid_dimensions(dimensions):
        return redirect('/')

    sql_filter = Tire.sql_filter(**dimensions)


    selected = { v: 'selected' for k,v in dimensions.items() }


    context = {}
    context['base_url'] = Util.BASE_URL
    context['tires'] = []
    hint = ''
    if selected:
        hint = 'No tires found matching your search criterion'
        context['tires'] = StatsPresenter(sql_filter).tire_stats_sorted('', False)
    context['hint'] = hint
    context['selected'] = selected



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
