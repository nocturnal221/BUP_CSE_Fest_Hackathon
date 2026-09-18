from django.contrib import admin
from .models import BatteryConfig, OptimizationScenario, HourlyPlanRecord, DirectiveRecord

# Pro Admin Panel Branding
admin.site.site_header = "GridWise — Smart Campus Energy Admin"
admin.site.site_title = "GridWise Admin Portal"
admin.site.index_title = "Microgrid Optimization & Battery Management Dashboard"


class HourlyPlanInline(admin.TabularInline):
    model = HourlyPlanRecord
    extra = 0
    can_delete = False
    fields = ('hour', 'grid_kwh', 'solar_used_kwh', 'battery_action', 'battery_kwh', 'battery_energy_after_kwh')
    readonly_fields = fields


class DirectiveInline(admin.StackedInline):
    model = DirectiveRecord
    extra = 0
    can_delete = False
    fields = ('note_index', 'raw_note', 'applies', 'directive_type', 'structured_adjustment', 'explanation')
    readonly_fields = fields


@admin.register(OptimizationScenario)
class OptimizationScenarioAdmin(admin.ModelAdmin):
    list_display = ('scenario_id', 'total_cost_bdt', 'total_grid_kwh', 'peak_grid_kwh', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('scenario_id', 'plan_summary')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DirectiveInline, HourlyPlanInline]
    fieldsets = (
        ("Scenario Overview", {
            "fields": ("scenario_id", "plan_summary", "raw_operator_notes")
        }),
        ("Optimization Key Metrics", {
            "fields": ("total_cost_bdt", "total_grid_kwh", "peak_grid_kwh", "battery_capacity_kwh")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(BatteryConfig)
class BatteryConfigAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'capacity_kwh',
        'initial_energy_kwh',
        'minimum_energy_kwh',
        'max_charge_kwh_per_hour',
        'max_discharge_kwh_per_hour',
        'created_at'
    )
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Battery Identity", {
            "fields": ("name",)
        }),
        ("Capacity & Energy Limits", {
            "fields": ("capacity_kwh", "initial_energy_kwh", "minimum_energy_kwh")
        }),
        ("Power Rate Limits", {
            "fields": ("max_charge_kwh_per_hour", "max_discharge_kwh_per_hour")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(HourlyPlanRecord)
class HourlyPlanRecordAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'hour', 'grid_kwh', 'solar_used_kwh', 'battery_action', 'battery_kwh', 'battery_energy_after_kwh')
    list_filter = ('battery_action', 'hour')
    search_fields = ('scenario__scenario_id',)


@admin.register(DirectiveRecord)
class DirectiveRecordAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'note_index', 'directive_type', 'applies', 'explanation')
    list_filter = ('directive_type', 'applies')
    search_fields = ('scenario__scenario_id', 'raw_note', 'explanation')
