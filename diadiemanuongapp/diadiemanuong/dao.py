from django.db.models import Count
from .models import Category, Restaurant, Dish

def load_restaurant(params = {}):
    q = Restaurant.objects.all()

    kw = params.get('kw')
    if kw:
        q = q.objects.filter(name__icontains=kw)

    cate_id = params.get('cate_id')
    if cate_id:
        q = q.objects.filter(category_id=cate_id)


def load_dish(params = {}):
    q = Dish.objects.all()

    kw = params.get('kw')
    if kw:
        q = q.objects.filter(name__icontains=kw)

    cate_id = params.get('cate_id')
    if cate_id:
        q = q.objects.filter(category_id=cate_id)


def count_restaurant_by_cat():
    return Category.objects.annotate(count = Count('restaurants__id')).values('id', 'name', 'count').order_by('-count')