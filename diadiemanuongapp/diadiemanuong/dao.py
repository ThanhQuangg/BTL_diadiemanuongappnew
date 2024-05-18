from .models import Category, Restaurant, Dish, OrderDetail, Order
from datetime import datetime, timedelta

from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import ExtractMonth, ExtractYear, TruncMonth, TruncQuarter
from .serializer import DishSerializer, OrderDetailSerializer


def load_restaurant(params={}):
    q = Restaurant.objects.all()

    kw = params.get('kw')
    if kw:
        q = q.objects.filter(name__icontains=kw)

    cate_id = params.get('cate_id')
    if cate_id:
        q = q.objects.filter(category_id=cate_id)


def load_dish(params={}):
    q = Dish.objects.all()

    kw = params.get('kw')
    if kw:
        q = q.objects.filter(name__icontains=kw)

    cate_id = params.get('cate_id')
    if cate_id:
        q = q.objects.filter(category_id=cate_id)


def count_restaurant_by_cat():
    return Category.objects.annotate(count=Count('restaurants__id')).values('id', 'name', 'count').order_by('-count')


def get_monthly_revenue(restaurant_ids, year):
    monthly_revenue = (
        Order.objects.filter(restaurant_id=restaurant_ids, order_date__year=year)
        .annotate(month=TruncMonth('order_date'))
        .values('restaurant_id', 'month')
        .annotate(total_revenue=Sum('total_amount', output_field=FloatField()))
        .order_by('restaurant_id', 'month')
    )
    return monthly_revenue


def get_quarterly_revenue(restaurant_id, year):
    quarterly_revenue = (
        Order.objects.filter(restaurant_id=restaurant_id, order_date__year=year)
        .annotate(quarter=TruncQuarter('order_date'))
        .values('quarter')
        .annotate(total_revenue=Sum('total_amount', output_field=FloatField()))
        .order_by('quarter')
    )
    return quarterly_revenue


def get_yearly_revenue(restaurant_id, year):
    yearly_revenue = (
        Order.objects.filter(restaurant_id=restaurant_id, order_date__year=year)
        .annotate(year=ExtractYear('order_date'))
        .values('year')
        .annotate(total_revenue=Sum('total_amount', output_field=FloatField()))
        .order_by('year')
    )
    return yearly_revenue


def calculate_monthly_revenue_for_dishes(restaurant_id, year, month):
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1)

    dishes = Dish.objects.filter(restaurant_id=restaurant_id)

    monthly_revenue = []
    for dish in dishes:
        dish_revenue = OrderDetail.objects.filter(
            dish=dish,
            order__restaurant_id=restaurant_id,
            order__order_date__range=[start_date, end_date]
        ).aggregate(total_revenue=Sum(F('quantity') * F('total')))['total_revenue'] or 0

        monthly_revenue.append({
            'dish_id': dish.id,
            'dish_name': dish.name,
            'total_revenue': dish_revenue
        })

    return monthly_revenue


def calculate_quarterly_revenue_for_dishes(restaurant_id, year, quarter):
    quarters = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    start_month = quarters[quarter][0]
    end_month = quarters[quarter][-1]

    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, 1) + timedelta(days=31)

    dishes = Dish.objects.filter(restaurant_id=restaurant_id)

    quarterly_revenue = []
    for dish in dishes:
        dish_revenue = OrderDetail.objects.filter(
            dish=dish,
            order__restaurant_id=restaurant_id,
            order__order_date__range=[start_date, end_date]
        ).aggregate(total_revenue=Sum(F('quantity') * F('total')))['total_revenue'] or 0

        quarterly_revenue.append({
            'dish_id': dish.id,
            'dish_name': dish.name,
            'total_revenue': dish_revenue
        })

    return quarterly_revenue


def calculate_yearly_revenue_for_dishes(restaurant_id, year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    dishes = Dish.objects.filter(restaurant_id=restaurant_id)

    yearly_revenue = []
    for dish in dishes:
        dish_revenue = OrderDetail.objects.filter(
            dish=dish,
            order__restaurant_id=restaurant_id,
            order__order_date__range=[start_date, end_date]
        ).aggregate(total_revenue=Sum(F('quantity') * F('total')))['total_revenue'] or 0

        yearly_revenue.append({
            'dish_id': dish.id,
            'dish_name': dish.name,
            'total_revenue': dish_revenue
        })

    return yearly_revenue