from django.urls import path

from . import views

app_name = 'route'
urlpatterns = [
    path('', views.route_filter, name='index'),
    path('add_route', views.route_add, name='add_route'),
    path('<int:id>', views.route_detail, name='route'),
    path('<int:id>/add_event', views.route_add_event, name='add_event'),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location'),
    path('<int:id>/reviews', views.route_reviews, name='route_reviews')

]