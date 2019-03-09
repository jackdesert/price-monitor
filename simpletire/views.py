# It appears you can also use shortcuts:


from django.shortcuts import render
from simpletire.models import Catalog
from simpletire.models import StatsPresenter
from simpletire.models import Tire
from simpletire.models import Util
import ipdb

def stats_view(request):

    regex = Tire.filter_by_size_regex( section_width  = request.GET.get('section_width'),
                                       profile        = request.GET.get('profile'),
                                       wheel_diameter = request.GET.get('wheel_diameter'))

    sql_filter = f"WHERE path ~ '{regex}'"

    context = {}
    context['base_url'] = Util.BASE_URL
    context['tires'] = StatsPresenter(sql_filter).tire_stats_sorted('', False)

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
