from rest_framework.pagination import PageNumberPagination

class RestaurantPaginator(PageNumberPagination):
    page_size = 2


class DishPaginator(PageNumberPagination):
    page_size = 5


class UserPaginator(PageNumberPagination):
    page_size = 4