from django.urls import path
from .views import (
    HealthView,
    OptimizeEnergyView,
    BatteryConfigListCreateView,
    BatteryConfigDetailView,
    OptimizationScenarioListView,
    OptimizationScenarioDetailView,
)

urlpatterns = [
    # Core Hackathon Pipeline Endpoints
    path('health', HealthView.as_view(), name='health'),
    path('optimize-energy', OptimizeEnergyView.as_view(), name='optimize-energy'),

    # Public Generic API Endpoints (Explicit DRF Generic Views)
    path('api/battery-configs/', BatteryConfigListCreateView.as_view(), name='battery-config-list'),
    path('api/battery-configs/<int:pk>/', BatteryConfigDetailView.as_view(), name='battery-config-detail'),
    path('api/scenarios/', OptimizationScenarioListView.as_view(), name='scenario-list'),
    path('api/scenarios/<int:pk>/', OptimizationScenarioDetailView.as_view(), name='scenario-detail'),
]
