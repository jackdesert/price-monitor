# It appears you can also use shortcuts:


from django.shortcuts import render
from django.shortcuts import redirect
from random import SystemRandom
from datetime import datetime
from simpletire.models import Catalog
from simpletire.models import Reading
from simpletire.models import StatsPresenter
from simpletire.models import Tire
from simpletire.models import Util
import pdb

MAX_TIRES = 200

def status_view(request):
    context = {}
    context['most_recent_reading'] = Reading.most_recent()

    return render(request, 'status.jinja2', context)


def index_view(request):
    dimensions = {}
    for dimension in Tire.DIMENSIONS:
        value = request.GET.get(dimension)
        if value:
            dimensions[dimension] = int(value)

    if not Tire.valid_dimensions(dimensions):
        return redirect('/')

    sql_filter = Tire.sql_filter(**dimensions)


    selected = { v: 'selected' for k,v in dimensions.items() }

    label = label_from_dimensions(dimensions)

    show_all = bool(request.GET.get('show_all'))

    if show_all:
        limit = 0
    else:
        limit = MAX_TIRES


    matching_records_count = None
    no_matching_tires_hint = ''
    tires = []
    if selected:
        no_matching_tires_hint = 'No tires found matching your search criteria'
        stats_presenter = StatsPresenter(sql_filter, limit)
        tires = stats_presenter.tire_stats()
        matching_records_count = stats_presenter.matching_records_count()

    show_all_path = ''
    if (len(tires) == MAX_TIRES) and not show_all:
        show_all_path = f'{request.get_full_path_info()}&show_all=true'


    photos = ['car2-trimmed-photo-by-Andrea-Lynn--Jarrett-Matthews.jpg',
              'car4-trimmed-narrow--Mario-Martinez.jpg',
              'car5-trimmed--Chris-Burgunder.jpg',
              'car6-trimmed--Chris-Burgunder.jpg']

    shuffler = SystemRandom(datetime.now().microsecond)
    shuffler.shuffle(photos)



    context = {}
    context['base_url'] = Util.BASE_URL
    context['random_photo'] = photos[0]
    context['matching_records_count'] = matching_records_count
    context['show_all_path'] = show_all_path
    context['tires'] = tires
    context['max_tires'] = MAX_TIRES
    context['no_matching_tires_hint'] = no_matching_tires_hint
    context['label'] = label
    context['selected'] = selected

    return render(request, 'index.jinja2', context)





def label_from_dimensions(dimensions):
    output = ''
    if dimensions.get('wheel_diameter'):
        output = f"{dimensions['wheel_diameter']}-inch Tires"
    else:
        output = 'Tires'

    conjunction = 'with'
    if dimensions.get('section_width'):
        output += f" at least {dimensions['section_width']} wide"
        conjunction = 'and'
    if dimensions.get('aspect_ratio'):
        output += f" {conjunction} aspect ratio near {dimensions['aspect_ratio']}"

    return output


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
