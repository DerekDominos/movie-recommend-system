from django import template
from recommend.models import Movie

register = template.Library()

@register.inclusion_tag('recommend/sidebar.html')
def sidebar_movies():
    movies = Movie.objects.order_by('-click_count')[:10]
    return {'movies': movies}