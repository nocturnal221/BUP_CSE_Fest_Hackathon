from rest_framework import serializers
from .models import BatteryConfig, OptimizationScenario, HourlyPlanRecord, DirectiveRecord


# ==========================================
# In-Memory Optimization Pipeline Serializers
# ==========================================

class HourInputSerializer(serializers.Serializer):
    hour = serializers.IntegerField(min_value=0, max_value=23)
    demand_kwh = serializers.FloatField(min_value=0.0)
    solar_kwh = serializers.FloatField(min_value=0.0)
    tariff_bdt_per_kwh = serializers.FloatField(min_value=0.0)


class BatteryInputSerializer(serializers.Serializer):
    capacity_kwh = serializers.FloatField(min_value=0.0)
    initial_energy_kwh = serializers.FloatField(min_value=0.0)
    minimum_energy_kwh = serializers.FloatField(min_value=0.0)
    max_charge_kwh_per_hour = serializers.FloatField(min_value=0.0)
    max_discharge_kwh_per_hour = serializers.FloatField(min_value=0.0)

    def validate(self, data):
        if data['initial_energy_kwh'] > data['capacity_kwh']:
            raise serializers.ValidationError("initial_energy_kwh cannot exceed capacity_kwh.")
        if data['minimum_energy_kwh'] > data['capacity_kwh']:
            raise serializers.ValidationError("minimum_energy_kwh cannot exceed capacity_kwh.")
        if data['initial_energy_kwh'] < data['minimum_energy_kwh']:
            raise serializers.ValidationError("initial_energy_kwh cannot be less than minimum_energy_kwh.")
        return data


class ScenarioRequestSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(max_length=255)
    operator_notes = serializers.ListField(
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        min_length=1,
        max_length=3
    )
    hours = serializers.ListField(
        child=HourInputSerializer(),
        min_length=24,
        max_length=24
    )
    battery = BatteryInputSerializer()

    def validate_hours(self, value):
        hours_seen = [item['hour'] for item in value]
        if set(hours_seen) != set(range(24)):
            raise serializers.ValidationError("hours must contain exactly 24 entries covering hours 0 through 23.")
        return sorted(value, key=lambda x: x['hour'])


class DirectiveInterpretationSerializer(serializers.Serializer):
    note_index = serializers.IntegerField(min_value=0)
    applies = serializers.BooleanField()
    directive_type = serializers.ChoiceField(choices=[
        "solar_reduction",
        "minimum_battery_reserve",
        "no_charge_window",
        "no_discharge_window",
        "max_grid_window",
        "no_op"
    ])
    structured_adjustment = serializers.DictField(allow_null=True, required=False)
    explanation = serializers.CharField(allow_blank=True)


class HourlyPlanItemSerializer(serializers.Serializer):
    hour = serializers.IntegerField(min_value=0, max_value=23)
    grid_kwh = serializers.FloatField(min_value=0.0)
    solar_used_kwh = serializers.FloatField(min_value=0.0)
    battery_action = serializers.ChoiceField(choices=["charge", "discharge", "idle"])
    battery_kwh = serializers.FloatField(min_value=0.0)
    battery_energy_after_kwh = serializers.FloatField(min_value=0.0)


class ScenarioResponseSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(max_length=255)
    directive_interpretation = serializers.ListField(child=DirectiveInterpretationSerializer())
    hourly_plan = serializers.ListField(child=HourlyPlanItemSerializer(), min_length=24, max_length=24)
    total_grid_kwh = serializers.FloatField()
    total_cost_bdt = serializers.FloatField()
    peak_grid_kwh = serializers.FloatField()
    plan_summary = serializers.CharField()


# ==========================================
# DRF ModelSerializers for ModelViewSets
# ==========================================

class BatteryConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryConfig
        fields = '__all__'


class HourlyPlanRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyPlanRecord
        fields = '__all__'


class DirectiveRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectiveRecord
        fields = '__all__'


class OptimizationScenarioSerializer(serializers.ModelSerializer):
    hourly_plans = HourlyPlanRecordSerializer(many=True, read_only=True)
    directives = DirectiveRecordSerializer(many=True, read_only=True)

    class Meta:
        model = OptimizationScenario
        fields = '__all__'
