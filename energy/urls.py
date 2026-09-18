from django.urls import path
from .views import HealthView, OptimizeEnergyView

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('optimize-energy', OptimizeEnergyView.as_view(), name='optimize-energy'),
]
