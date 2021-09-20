from django.urls import path

from rest_framework.routers import DefaultRouter

from core import views


app_name = "core"


urlpatterns = [
    path('', views.CoinView.as_view()),
]


router = DefaultRouter()
router.register(r'inventory', views.InventoryViewSet, basename='inventory')
urlpatterns += router.urls
