# It appears you can also use shortcuts:


from django.shortcuts import render
from django.shortcuts import redirect
from random import randint
from simpletire.models import Catalog
from simpletire.models import StatsPresenter
from simpletire.models import Tire
from simpletire.models import Util
import ipdb

def stats_view(request):
    max_tires = 200
    dimensions = {}
    for dimension in Tire.DIMENSIONS:
        value = request.GET.get(dimension)
        if value:
            dimensions[dimension] = int(value)

    if not Tire.valid_dimensions(dimensions):
        return redirect('/')

    sql_filter = Tire.sql_filter(**dimensions)


    selected = { v: 'selected' for k,v in dimensions.items() }

    label = ''
    if dimensions.get('wheel_diameter'):
        label = f"{dimensions['wheel_diameter']}-inch Tires"
    else:
        label = 'Tires'

    conjunction = 'with'
    conjunction = 'with'
    if dimensions.get('section_width'):
        label += f" at least {dimensions['section_width']} wide"
        conjunction = 'and'
    if dimensions.get('aspect_ratio'):
        label += f" {conjunction} aspect ratio near {dimensions['aspect_ratio']}"



    context = {}
    context['base_url'] = Util.BASE_URL
    hint = ''
    tires = []
    available_records = 0
    if selected:
        hint = 'No tires found matching your search criteria'
        tires = StatsPresenter(sql_filter).tire_stats_sorted('', False)
        available_records = len(tires)
    show_all_path = ''
    if (len(tires) > max_tires) and not request.GET.get('show_all'):
        tires = tires[0:max_tires]
        show_all_path = f'{request.get_full_path_info()}&show_all=true'


    random_photos = ['car2-trimmed.jpg', 'car4-trimmed.jpg', 'car5-trimmed.jpg', 'car6-trimmed.jpg']
    photo_index = randint(0, len(random_photos) - 1)
    context['random_photo'] = random_photos[photo_index]

    context['available_records'] = available_records
    context['show_all_path'] = show_all_path
    context['tires'] = tires
    context['max_tires'] = max_tires
    context['hint'] = hint
    context['label'] = label
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
