from django.urls import path, include
from . import views
from rest_framework import routers
from .views import request_activation, review_activation_requests, update_activation_request, activation_request_success

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
router.register('roles', views.RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
path('request-activation/', request_activation, name='request_activation'),
    path('request-activation/', request_activation, name='request_activation'),
    path('review-activation-requests/', review_activation_requests, name='review_activation_requests'),
    path('update-activation-request/<int:request_id>/<str:status>/', update_activation_request,
         name='update_activation_request'),
    path('activation-request-success/', activation_request_success, name='activation_request_success'),

]