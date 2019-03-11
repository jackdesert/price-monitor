# It appears you can also use shortcuts:


from django.shortcuts import render
from django.shortcuts import redirect
from simpletire.models import Catalog
from simpletire.models import StatsPresenter
from simpletire.models import Tire
from simpletire.models import Util
import ipdb

def stats_view(request):
    section_width  = request.GET.get('section_width')
    aspect_ratio        = request.GET.get('aspect_ratio')
    wheel_diameter = request.GET.get('wheel_diameter')

    # TODO build a method that checks these lengths
    error = False
    if section_width and len(section_width) != 3:
        error = True
    if aspect_ratio and len(aspect_ratio) != 2:
        error = True
    if wheel_diameter and len(wheel_diameter) != 2:
        error = True


    if error:
        return redirect('/')

    regex = Tire.filter_by_size_regex( section_width  = section_width,
                                       aspect_ratio        = aspect_ratio,
                                       wheel_diameter = wheel_diameter )

    sql_filter = f"WHERE path ~ '{regex}'"


    selected = {}
    if section_width:
        selected[int(section_width)]  = 'selected'
    if aspect_ratio:
        selected[int(aspect_ratio)]        = 'selected'
    if wheel_diameter:
        selected[int(wheel_diameter)] = 'selected'

    context = {}
    context['base_url'] = Util.BASE_URL
    context['tires'] = []
    hint = ''
    if section_width or aspect_ratio or wheel_diameter:
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
