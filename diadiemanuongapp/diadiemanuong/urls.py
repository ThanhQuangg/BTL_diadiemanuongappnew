from django.urls import path, include
from . import views
from rest_framework import routers




router = routers.DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('restaurants', views.RestaurantViewSet, basename='restaurants')
router.register('dishes', views.DishViewSet, basename='dishes')
router.register('users', views.UserViewSet, basename='users')
router.register('comments', views.CommentViewSet, basename='comments')
router.register('ratings', views.RatingViewSet, basename='ratings')
router.register('orders', views.OrderViewSet, basename='orders')
router.register('order-details', views.OrderDetailViewSet, basename='order-details')
router.register('paymentTypes', views.PaymentViewSet)


urlpatterns = [
    path('', include(router.urls)),

]