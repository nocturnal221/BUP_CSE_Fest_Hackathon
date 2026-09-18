from django.db import models


class BatteryConfig(models.Model):
    """Stores microgrid battery storage configurations and operational limits."""
    name = models.CharField(max_length=120, default="Campus Main Battery", help_text="Identifier for the battery unit")
    capacity_kwh = models.FloatField(default=220.0, help_text="Total energy storage capacity in kWh")
    initial_energy_kwh = models.FloatField(default=110.0, help_text="Starting energy at hour 0 in kWh")
    minimum_energy_kwh = models.FloatField(default=40.0, help_text="Baseline reserve threshold in kWh")
    max_charge_kwh_per_hour = models.FloatField(default=50.0, help_text="Max charge speed per hour")
    max_discharge_kwh_per_hour = models.FloatField(default=50.0, help_text="Max discharge speed per hour")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Battery Configuration"
        verbose_name_plural = "Battery Configurations"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.capacity_kwh} kWh)"


class OptimizationScenario(models.Model):
    """Audit log and record of 24-hour campus energy optimization runs."""
    scenario_id = models.CharField(max_length=255, db_index=True)
    total_grid_kwh = models.FloatField(default=0.0, verbose_name="Total Grid Import (kWh)")
    total_cost_bdt = models.FloatField(default=0.0, verbose_name="Total Cost (BDT)")
    peak_grid_kwh = models.FloatField(default=0.0, verbose_name="Peak Grid Draw (kWh)")
    plan_summary = models.TextField(blank=True, default="")
    battery_capacity_kwh = models.FloatField(null=True, blank=True)
    raw_operator_notes = models.JSONField(default=list, blank=True, help_text="Input operator notes list")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Optimization Scenario"
        verbose_name_plural = "Optimization Scenarios"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.scenario_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class HourlyPlanRecord(models.Model):
    """Hourly optimized schedule breakdown (hours 0 through 23)."""
    ACTION_CHOICES = [
        ('charge', 'Charge'),
        ('discharge', 'Discharge'),
        ('idle', 'Idle'),
    ]

    scenario = models.ForeignKey(OptimizationScenario, on_delete=models.CASCADE, related_name='hourly_plans')
    hour = models.IntegerField(verbose_name="Hour of Day (0-23)")
    grid_kwh = models.FloatField(default=0.0, verbose_name="Grid Import (kWh)")
    solar_used_kwh = models.FloatField(default=0.0, verbose_name="Solar Energy Used (kWh)")
    battery_action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='idle')
    battery_kwh = models.FloatField(default=0.0, verbose_name="Battery Charged / Discharged (kWh)")
    battery_energy_after_kwh = models.FloatField(default=0.0, verbose_name="Battery State of Charge (kWh)")

    class Meta:
        verbose_name = "Hourly Plan Entry"
        verbose_name_plural = "Hourly Plan Entries"
        ordering = ['scenario', 'hour']
        unique_together = ('scenario', 'hour')

    def __str__(self):
        return f"Hour {self.hour}: {self.battery_action} ({self.grid_kwh:.1f} kWh grid)"


class DirectiveRecord(models.Model):
    """Structured LLM directive interpretation generated for an operator note."""
    scenario = models.ForeignKey(OptimizationScenario, on_delete=models.CASCADE, related_name='directives')
    note_index = models.IntegerField(default=0)
    raw_note = models.TextField(blank=True, default="")
    applies = models.BooleanField(default=False)
    directive_type = models.CharField(max_length=50)
    structured_adjustment = models.JSONField(null=True, blank=True)
    explanation = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Directive Interpretation"
        verbose_name_plural = "Directive Interpretations"
        ordering = ['scenario', 'note_index']

    def __str__(self):
        status_label = "Applies" if self.applies else "No-Op"
        return f"Note {self.note_index} [{self.directive_type}] - {status_label}"
