from .models import Category, Restaurant, Dish, OrderDetail, Order
from datetime import datetime, timedelta

from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import ExtractMonth, ExtractYear
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


def get_order_count_in_month(month):
    # Chuyển đổi month thành một số nguyên (ví dụ: 1 cho tháng 1, 2 cho tháng 2, ...)
    month = int(month)

    # Xác định ngày đầu tiên của tháng được chỉ định
    start_date = datetime(year=datetime.now().year, month=month, day=1)

    # Xác định ngày cuối cùng của tháng được chỉ định
    if month == 12:
        end_date = datetime(year=datetime.now().year + 1, month=1, day=1)
    else:
        end_date = datetime(year=datetime.now().year, month=month + 1, day=1)

    # Sử dụng filter để lấy tất cả các đơn hàng trong khoảng thời gian này
    orders_in_month = Order.objects.filter(created_date__gte=start_date, created_date__lt=end_date)

    # Đếm số lượng đơn hàng
    order_count = orders_in_month.count()

    return order_count


def get_order_count_in_year(year):
    # Chuyển đổi year thành một số nguyên
    year = int(year)

    # Xác định ngày đầu tiên và ngày cuối cùng của năm được chỉ định
    start_date = datetime(year=year, month=1, day=1)
    end_date = datetime(year=year + 1, month=1, day=1)

    # Sử dụng filter để lấy tất cả các đơn hàng trong khoảng thời gian này
    orders_in_year = Order.objects.filter(created_date__gte=start_date, created_date__lt=end_date)

    # Đếm số lượng đơn hàng
    order_count = orders_in_year.count()

    return order_count


def get_order_count_in_quarter(quarter, year):
    # Chuyển đổi quarter và year thành các số nguyên
    quarter = int(quarter)
    year = int(year)

    # Xác định tháng đầu tiên và tháng cuối cùng của quý được chỉ định
    if quarter == 1:
        start_month = 1
        end_month = 4
    elif quarter == 2:
        start_month = 4
        end_month = 7
    elif quarter == 3:
        start_month = 7
        end_month = 10
    elif quarter == 4:
        start_month = 10
        end_month = 13

    # Xác định ngày đầu tiên và ngày cuối cùng của quý được chỉ định
    start_date = datetime(year=year, month=start_month, day=1)
    end_date = datetime(year=year, month=end_month, day=1)

    # Sử dụng filter để lấy tất cả các đơn hàng trong khoảng thời gian này
    orders_in_quarter = Order.objects.filter(created_date__gte=start_date, created_date__lt=end_date)

    # Đếm số lượng đơn hàng
    order_count = orders_in_quarter.count()

    return order_count


##=================================================##seller - stast dish and category


def dish_revenue_statistics_in_month(restaurant_id, dish_id, year):
    data = []

    dish_name = Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id).values('name_dish').first()

    if dish_name:
        dish_name = dish_name['name_dish']
        monthly_data = []

        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            end_date = start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1)

            dish_revenue = (
                    Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id,
                                        orderdetail__order__created_at__date__range=[start_date, end_date])
                                        #orderdetail__order__status_pay=True)
                    .annotate(
                        total_revenue=ExpressionWrapper(
                            Sum(F('orderdetail__quantity') * F('price'), output_field=FloatField()),
                            output_field=FloatField()
                        ),
                        total_quantity=Sum('orderdetail__quantity')
                    )
                    .values('id', 'name_dish', 'total_revenue', 'total_quantity')
                    .first() or {'total_revenue': 0, 'total_quantity': 0}
            )

            monthly_data.append({
                'id': dish_id,
                'name_dish': dish_name,
                'total_revenue': dish_revenue['total_revenue'],
                'total_quantity': dish_revenue['total_quantity'],
                'month': month
            })

        data.extend(monthly_data)

    return data


def dish_revenue_statistics_in_year(restaurant_id, year, dish_id):
    data = []
    dish_name = Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id).values('name_dish').first()

    if dish_name:
        dish_name = dish_name['name_dish']
        yearly_data = []

        current_year = datetime.now().year
        start_year = year

        for year in range(start_year, current_year + 1):
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)

            dish_revenue = (
                    Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id,
                                           orderdetail__order__created_at__date__range=[start_date, end_date])
                                           #orderdetail__order__status_pay=True)
                    .annotate(
                        total_revenue=ExpressionWrapper(
                            Sum(F('orderdetail__quantity') * F('price'), output_field=FloatField()),
                            output_field=FloatField()
                        ),
                        total_quantity=Sum('orderdetail__quantity')
                    )
                    .values('id', 'name_dish', 'total_revenue', 'total_quantity')
                    .first() or {'total_revenue': 0, 'total_quantity': 0}
            )

            yearly_data.append({
                'id': dish_id,
                'name_dish': dish_name,
                'total_revenue': dish_revenue['total_revenue'],
                'total_quantity': dish_revenue['total_quantity'],
            })
        data.extend(yearly_data)
    return data


def dish_revenue_statistics_in_quarter(restaurant_id, year, dish_id):
    data = []
    dish_name = Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id).values('name_dish').first()

    if dish_name:
        dish_name = dish_name['name_dish']
        quarterly_data = []

        for quarter in range(1, 5):
            start_date = datetime(year, (quarter - 1) * 3 + 1, 1)
            # Tính toán ngày cuối cùng của quý
            end_date = start_date.replace(month=start_date.month + 2) + timedelta(days=30)

            dish_revenue = (
                Dish.objects.filter(id=dish_id, restaurant_id=restaurant_id,
                                       orderdetail__order__created_at__date__range=[start_date, end_date])
                                      # orderdetail__order__status_pay=True)
                .annotate(
                    total_revenue=ExpressionWrapper(
                        Sum(F('orderdetail__quantity') * F('price'), output_field=FloatField()),
                        output_field=FloatField()
                    ),
                    total_quantity=Sum('orderdetail__quantity')
                )
                .values('id', 'name_dish', 'total_revenue', 'total_quantity')
                .first()
            )

            if dish_revenue is None:
                dish_revenue = {'total_revenue': 0, 'total_quantity': 0}

            quarterly_data.append({
                'id': dish_id,
                'name_dish': dish_name,
                'total_revenue': dish_revenue['total_revenue'],
                'total_quantity': dish_revenue['total_quantity'],
            })
        data.extend(quarterly_data)
    return data




##=================================================##manager - stats count dish


def dish_count_statistics_in_month(restaurant, year):
    monthly_stats = (
        Dish.objects
        .annotate(month=ExtractMonth('created_at'))
        .filter(created_at__year=year, restaurant=restaurant, status=True)
        .values('month')
        .annotate(
            total_dishes=Count('id'),
        )
    )

    all_months_stats = [
        {
            'month': month,
            'total_dishes': 0,
            'dish_info': []
        } for month in range(1, 13)
    ]

    total_dishes_all_months = 0

    for stats in monthly_stats:
        month = stats['month']
        dishes = Dish.objects.filter(created_at__year=year, created_at__month=month, restaurant=restaurant)
        dish_info = DishSerializer(dishes, many=True).data

        total_dishes_all_months += stats['total_dishes']

        all_months_stats[month - 1].update({
            'total_dishes': stats['total_dishes'],
            'dish_info': dish_info,
        })

    return {
        'total_dishes_all_months': total_dishes_all_months,
        'monthly_stats': all_months_stats,
    }


def dish_count_statistics_in_quarter(restaurant, year):
    quarterly_stats = []
    total_dishes_all_quarters = 0

    for quarter in range(1, 5):
        start_date = datetime(year, (quarter - 1) * 3 + 1, 1)
        end_date = start_date.replace(month=start_date.month + 2) + timedelta(days=30)

        dishes = Dish.objects.filter(
            created_at__year=year,
            created_at__month__in=[(quarter - 1) * 3 + 1, (quarter - 1) * 3 + 2, (quarter - 1) * 3 + 3],
            restaurant=restaurant,
            #status=True
        )

        dish_info = DishSerializer(dishes, many=True).data

        total_dishes = dishes.count()

        total_dishes_all_quarters += total_dishes

        quarterly_stats.append({
            'quarter': quarter,
            'total_dishes': total_dishes,
            'dish_info': dish_info,
        })

    return {
        'total_dishes_all_quarters': total_dishes_all_quarters,
        'quarterly_stats': quarterly_stats,
    }


##=================================================##manager - count order


def order_count_statistics_in_month(restaurant_id, year):
    monthly_stats = (
        OrderDetail.objects
        .filter(dish__restaurant_id=restaurant_id, order__created_at__year=year)
        .annotate(month=ExtractMonth('order__created_at'))
        .values('month')
        .annotate(
            total_orders=Count('order__id'),
        )
    )

    all_months_stats = [
        {
            'month': month,
            'total_orders': 0,
            'order_info': []
        } for month in range(1, 13)
    ]

    for stats in monthly_stats:
        month = stats['month']
        orders = OrderDetail.objects.filter(
            dish__restaurant_id=restaurant_id,
            order__created_at__year=year,
            order__created_at__month=month
        )

        order_info = OrderDetailSerializer(orders, many=True).data

        all_months_stats[month - 1].update({
            'total_orders': stats['total_orders'],
            'order_info': order_info,
        })

    return {
        'monthly_stats': all_months_stats,
    }


def order_count_statistics_in_quarter(restaurant_id, year):
    try:
        year = int(year)
    except ValueError:
        return {'quarterly_stats': []}

    quarterly_stats = []

    for quarter in range(1, 5):
        start_date = datetime(year, (quarter - 1) * 3 + 1, 1)
        end_date = start_date.replace(month=start_date.month + 2) + timedelta(days=30)

        orders = OrderDetail.objects.filter(
            dish__restaurant_id=restaurant_id,
            order__created_at__range=[start_date, end_date]
        )

        order_info = OrderDetailSerializer(orders, many=True).data

        total_orders = orders.count()

        quarterly_stats.append({
            'quarter': quarter,
            'total_orders': total_orders,
            'order_info': order_info,
        })

    return {
        'quarterly_stats': quarterly_stats,
    }
