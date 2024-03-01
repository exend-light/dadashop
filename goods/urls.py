from django.urls import path
from . import views
urlpatterns=[
    path('index',views.index),

    path('catalogs/<int:id>',views.catalogs),
    path('detail/<int:id>',views.detail),
    path('sku',views.sku),
    path('search',views.search)
]
