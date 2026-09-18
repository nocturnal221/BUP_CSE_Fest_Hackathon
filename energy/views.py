from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import BatteryConfig, OptimizationScenario
from .serializers import (
    ScenarioRequestSerializer,
    ScenarioResponseSerializer,
    BatteryConfigSerializer,
    OptimizationScenarioSerializer,
)
from .services.llm_interpreter import interpret_operator_notes
from .services.guardrail import validate_directive_interpretation
from .services.optimizer import optimize_schedule
from .services.replay_validator import replay_validate_schedule


class HealthView(generics.GenericAPIView):
    """
    Public Health & Liveness Probe endpoint.
    GET /health -> {"status": "ok"}
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class OptimizeEnergyView(generics.GenericAPIView):
    """
    Public 24-Hour Campus Energy Optimization Pipeline.
    POST /optimize-energy
    
    GenericAPIView adhering to the ScenarioRequestSerializer and ScenarioResponseSerializer schema.
    Pure in-memory LP optimization pipeline; no database writes are required.
    """
    permission_classes = [AllowAny]
    serializer_class = ScenarioRequestSerializer

    def post(self, request, *args, **kwargs):
        # 1. DRF Generic Schema Validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        scenario_id = validated_data['scenario_id']
        notes = validated_data['operator_notes']
        hours = validated_data['hours']
        battery = validated_data['battery']

        # 2. LLM Interpretation (OpenAI / High-Fidelity Fallback)
        raw_interpretations = interpret_operator_notes(notes, battery)

        # 3. Deterministic Guardrail Check
        directives = validate_directive_interpretation(raw_interpretations, len(notes), battery)

        # 4. LP Math Optimization (Google OR-Tools GLOP)
        optimization_result = optimize_schedule(hours, battery, directives)

        # 5. Independent Replay Validation
        replay_validate_schedule(
            hourly_plan=optimization_result['hourly_plan'],
            hours_data=hours,
            battery_data=battery,
            directives=directives
        )

        response_payload = {
            "scenario_id": scenario_id,
            "directive_interpretation": directives,
            "hourly_plan": optimization_result['hourly_plan'],
            "total_grid_kwh": optimization_result['total_grid_kwh'],
            "total_cost_bdt": optimization_result['total_cost_bdt'],
            "peak_grid_kwh": optimization_result['peak_grid_kwh'],
            "plan_summary": optimization_result['plan_summary']
        }

        response_serializer = ScenarioResponseSerializer(data=response_payload)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class BatteryConfigListCreateView(generics.ListCreateAPIView):
    """
    Public Generic List & Create API view for Battery Configurations.
    GET /api/battery-configs/
    POST /api/battery-configs/
    """
    queryset = BatteryConfig.objects.all()
    serializer_class = BatteryConfigSerializer
    permission_classes = [AllowAny]


class BatteryConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Public Generic Retrieve, Update & Destroy API view for a Battery Configuration.
    GET /api/battery-configs/<int:pk>/
    PUT / PATCH /api/battery-configs/<int:pk>/
    DELETE /api/battery-configs/<int:pk>/
    """
    queryset = BatteryConfig.objects.all()
    serializer_class = BatteryConfigSerializer
    permission_classes = [AllowAny]


class OptimizationScenarioListView(generics.ListAPIView):
    """
    Public Generic List API view for past optimization scenario audit records.
    GET /api/scenarios/
    """
    queryset = OptimizationScenario.objects.all()
    serializer_class = OptimizationScenarioSerializer
    permission_classes = [AllowAny]


class OptimizationScenarioDetailView(generics.RetrieveAPIView):
    """
    Public Generic Retrieve API view for a specific optimization scenario run.
    GET /api/scenarios/<int:pk>/
    """
    queryset = OptimizationScenario.objects.all()
    serializer_class = OptimizationScenarioSerializer
    permission_classes = [AllowAny]
