from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import ScenarioRequestSerializer, ScenarioResponseSerializer
from .services.llm_interpreter import interpret_operator_notes
from .services.guardrail import validate_directive_interpretation
from .services.optimizer import optimize_schedule
from .services.replay_validator import replay_validate_schedule


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class OptimizeEnergyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. DRF Schema Validation
        serializer = ScenarioRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        scenario_id = validated_data['scenario_id']
        notes = validated_data['operator_notes']
        hours = validated_data['hours']
        battery = validated_data['battery']

        # 2. LLM Interpretation (OpenAI / Deterministic Fallback)
        raw_interpretations = interpret_operator_notes(notes, battery)

        # 3. Deterministic Guardrail Check
        directives = validate_directive_interpretation(raw_interpretations, len(notes), battery)

        # 4. LP Math Optimization
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
