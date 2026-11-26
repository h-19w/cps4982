from django.urls import path 
from . import views 
app_name = 'minisearch'

urlpatterns = [  
path('search', views.search_index, name='search_view'),
path('', views.index),
path('read/<str:filename>', views.read),
]
