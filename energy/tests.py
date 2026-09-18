from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

HOURS_S1 = [
    {"hour": 0, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 1, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 2, "demand_kwh": 80, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 3, "demand_kwh": 80, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 4, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 5, "demand_kwh": 95, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 6, "demand_kwh": 110, "solar_kwh": 5, "tariff_bdt_per_kwh": 8},
    {"hour": 7, "demand_kwh": 130, "solar_kwh": 20, "tariff_bdt_per_kwh": 10},
    {"hour": 8, "demand_kwh": 150, "solar_kwh": 50, "tariff_bdt_per_kwh": 12},
    {"hour": 9, "demand_kwh": 165, "solar_kwh": 90, "tariff_bdt_per_kwh": 14},
    {"hour": 10, "demand_kwh": 175, "solar_kwh": 130, "tariff_bdt_per_kwh": 16},
    {"hour": 11, "demand_kwh": 180, "solar_kwh": 160, "tariff_bdt_per_kwh": 16},
    {"hour": 12, "demand_kwh": 185, "solar_kwh": 180, "tariff_bdt_per_kwh": 15},
    {"hour": 13, "demand_kwh": 180, "solar_kwh": 170, "tariff_bdt_per_kwh": 14},
    {"hour": 14, "demand_kwh": 170, "solar_kwh": 140, "tariff_bdt_per_kwh": 13},
    {"hour": 15, "demand_kwh": 165, "solar_kwh": 90, "tariff_bdt_per_kwh": 14},
    {"hour": 16, "demand_kwh": 170, "solar_kwh": 45, "tariff_bdt_per_kwh": 18},
    {"hour": 17, "demand_kwh": 185, "solar_kwh": 10, "tariff_bdt_per_kwh": 22},
    {"hour": 18, "demand_kwh": 205, "solar_kwh": 0, "tariff_bdt_per_kwh": 28},
    {"hour": 19, "demand_kwh": 215, "solar_kwh": 0, "tariff_bdt_per_kwh": 30},
    {"hour": 20, "demand_kwh": 205, "solar_kwh": 0, "tariff_bdt_per_kwh": 26},
    {"hour": 21, "demand_kwh": 175, "solar_kwh": 0, "tariff_bdt_per_kwh": 18},
    {"hour": 22, "demand_kwh": 135, "solar_kwh": 0, "tariff_bdt_per_kwh": 10},
    {"hour": 23, "demand_kwh": 105, "solar_kwh": 0, "tariff_bdt_per_kwh": 7}
]

HOURS_S2 = [
    {"hour": 0, "demand_kwh": 100, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 1, "demand_kwh": 95, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 2, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 4},
    {"hour": 3, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 4},
    {"hour": 4, "demand_kwh": 95, "solar_kwh": 0, "tariff_bdt_per_kwh": 4},
    {"hour": 5, "demand_kwh": 105, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 6, "demand_kwh": 120, "solar_kwh": 0, "tariff_bdt_per_kwh": 7},
    {"hour": 7, "demand_kwh": 135, "solar_kwh": 10, "tariff_bdt_per_kwh": 9},
    {"hour": 8, "demand_kwh": 145, "solar_kwh": 30, "tariff_bdt_per_kwh": 11},
    {"hour": 9, "demand_kwh": 155, "solar_kwh": 55, "tariff_bdt_per_kwh": 13},
    {"hour": 10, "demand_kwh": 165, "solar_kwh": 80, "tariff_bdt_per_kwh": 15},
    {"hour": 11, "demand_kwh": 175, "solar_kwh": 100, "tariff_bdt_per_kwh": 16},
    {"hour": 12, "demand_kwh": 180, "solar_kwh": 110, "tariff_bdt_per_kwh": 16},
    {"hour": 13, "demand_kwh": 175, "solar_kwh": 105, "tariff_bdt_per_kwh": 15},
    {"hour": 14, "demand_kwh": 165, "solar_kwh": 85, "tariff_bdt_per_kwh": 14},
    {"hour": 15, "demand_kwh": 160, "solar_kwh": 60, "tariff_bdt_per_kwh": 15},
    {"hour": 16, "demand_kwh": 170, "solar_kwh": 30, "tariff_bdt_per_kwh": 19},
    {"hour": 17, "demand_kwh": 190, "solar_kwh": 10, "tariff_bdt_per_kwh": 24},
    {"hour": 18, "demand_kwh": 210, "solar_kwh": 0, "tariff_bdt_per_kwh": 31},
    {"hour": 19, "demand_kwh": 220, "solar_kwh": 0, "tariff_bdt_per_kwh": 33},
    {"hour": 20, "demand_kwh": 210, "solar_kwh": 0, "tariff_bdt_per_kwh": 29},
    {"hour": 21, "demand_kwh": 180, "solar_kwh": 0, "tariff_bdt_per_kwh": 20},
    {"hour": 22, "demand_kwh": 145, "solar_kwh": 0, "tariff_bdt_per_kwh": 11},
    {"hour": 23, "demand_kwh": 115, "solar_kwh": 0, "tariff_bdt_per_kwh": 7}
]

HOURS_S4 = [
    {"hour": 0, "demand_kwh": 95, "solar_kwh": 0, "tariff_bdt_per_kwh": 7},
    {"hour": 1, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 2, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 3, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 4, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 5, "demand_kwh": 100, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 6, "demand_kwh": 115, "solar_kwh": 5, "tariff_bdt_per_kwh": 8},
    {"hour": 7, "demand_kwh": 130, "solar_kwh": 15, "tariff_bdt_per_kwh": 10},
    {"hour": 8, "demand_kwh": 145, "solar_kwh": 40, "tariff_bdt_per_kwh": 12},
    {"hour": 9, "demand_kwh": 155, "solar_kwh": 75, "tariff_bdt_per_kwh": 14},
    {"hour": 10, "demand_kwh": 165, "solar_kwh": 110, "tariff_bdt_per_kwh": 16},
    {"hour": 11, "demand_kwh": 175, "solar_kwh": 145, "tariff_bdt_per_kwh": 16},
    {"hour": 12, "demand_kwh": 180, "solar_kwh": 165, "tariff_bdt_per_kwh": 15},
    {"hour": 13, "demand_kwh": 175, "solar_kwh": 155, "tariff_bdt_per_kwh": 14},
    {"hour": 14, "demand_kwh": 170, "solar_kwh": 125, "tariff_bdt_per_kwh": 13},
    {"hour": 15, "demand_kwh": 165, "solar_kwh": 80, "tariff_bdt_per_kwh": 14},
    {"hour": 16, "demand_kwh": 175, "solar_kwh": 35, "tariff_bdt_per_kwh": 17},
    {"hour": 17, "demand_kwh": 195, "solar_kwh": 5, "tariff_bdt_per_kwh": 21},
    {"hour": 18, "demand_kwh": 215, "solar_kwh": 0, "tariff_bdt_per_kwh": 29},
    {"hour": 19, "demand_kwh": 225, "solar_kwh": 0, "tariff_bdt_per_kwh": 32},
    {"hour": 20, "demand_kwh": 215, "solar_kwh": 0, "tariff_bdt_per_kwh": 30},
    {"hour": 21, "demand_kwh": 185, "solar_kwh": 0, "tariff_bdt_per_kwh": 20},
    {"hour": 22, "demand_kwh": 150, "solar_kwh": 0, "tariff_bdt_per_kwh": 11},
    {"hour": 23, "demand_kwh": 120, "solar_kwh": 0, "tariff_bdt_per_kwh": 8}
]

HOURS_S6 = [
    {"hour": 0, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 1, "demand_kwh": 80, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 2, "demand_kwh": 80, "solar_kwh": 0, "tariff_bdt_per_kwh": 5},
    {"hour": 3, "demand_kwh": 80, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 4, "demand_kwh": 85, "solar_kwh": 0, "tariff_bdt_per_kwh": 6},
    {"hour": 5, "demand_kwh": 95, "solar_kwh": 0, "tariff_bdt_per_kwh": 7},
    {"hour": 6, "demand_kwh": 110, "solar_kwh": 5, "tariff_bdt_per_kwh": 8},
    {"hour": 7, "demand_kwh": 125, "solar_kwh": 20, "tariff_bdt_per_kwh": 9},
    {"hour": 8, "demand_kwh": 140, "solar_kwh": 55, "tariff_bdt_per_kwh": 11},
    {"hour": 9, "demand_kwh": 155, "solar_kwh": 100, "tariff_bdt_per_kwh": 13},
    {"hour": 10, "demand_kwh": 165, "solar_kwh": 150, "tariff_bdt_per_kwh": 15},
    {"hour": 11, "demand_kwh": 175, "solar_kwh": 190, "tariff_bdt_per_kwh": 16},
    {"hour": 12, "demand_kwh": 180, "solar_kwh": 210, "tariff_bdt_per_kwh": 16},
    {"hour": 13, "demand_kwh": 175, "solar_kwh": 200, "tariff_bdt_per_kwh": 15},
    {"hour": 14, "demand_kwh": 170, "solar_kwh": 160, "tariff_bdt_per_kwh": 14},
    {"hour": 15, "demand_kwh": 165, "solar_kwh": 100, "tariff_bdt_per_kwh": 15},
    {"hour": 16, "demand_kwh": 175, "solar_kwh": 50, "tariff_bdt_per_kwh": 18},
    {"hour": 17, "demand_kwh": 190, "solar_kwh": 15, "tariff_bdt_per_kwh": 22},
    {"hour": 18, "demand_kwh": 205, "solar_kwh": 0, "tariff_bdt_per_kwh": 27},
    {"hour": 19, "demand_kwh": 215, "solar_kwh": 0, "tariff_bdt_per_kwh": 29},
    {"hour": 20, "demand_kwh": 205, "solar_kwh": 0, "tariff_bdt_per_kwh": 27},
    {"hour": 21, "demand_kwh": 175, "solar_kwh": 0, "tariff_bdt_per_kwh": 18},
    {"hour": 22, "demand_kwh": 140, "solar_kwh": 0, "tariff_bdt_per_kwh": 10},
    {"hour": 23, "demand_kwh": 110, "solar_kwh": 0, "tariff_bdt_per_kwh": 7}
]


class GridWiseApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_sample_01(self):
        payload = {
            "scenario_id": "SAMPLE-01",
            "operator_notes": [
                "Facilities will wash the rooftop solar panels from noon until 2 PM. During cleaning, usable solar should be treated as roughly 25% of the forecast.",
                "The sports office moved next month's registration deadline."
            ],
            "hours": HOURS_S1,
            "battery": {
                "capacity_kwh": 220,
                "initial_energy_kwh": 110,
                "minimum_energy_kwh": 40,
                "max_charge_kwh_per_hour": 50,
                "max_discharge_kwh_per_hour": 50
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 38365.0, delta=1.0)
        self.assertAlmostEqual(d['total_grid_kwh'], 2692.5, delta=1.0)

    def test_sample_02(self):
        payload = {
            "scenario_id": "SAMPLE-02",
            "operator_notes": ["The battery charger will be isolated from 2 AM until 5 AM for electrical maintenance."],
            "hours": HOURS_S2,
            "battery": {
                "capacity_kwh": 200,
                "initial_energy_kwh": 70,
                "minimum_energy_kwh": 30,
                "max_charge_kwh_per_hour": 55,
                "max_discharge_kwh_per_hour": 55
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 42885.0, delta=1.0)
        self.assertAlmostEqual(d['total_grid_kwh'], 2915.0, delta=1.0)

    def test_sample_03(self):
        payload = {
            "scenario_id": "SAMPLE-03",
            "operator_notes": ["Keep at least 50% of the battery capacity stored in the battery from 6 PM until 9 PM for emergency operations."],
            "hours": HOURS_S1,
            "battery": {
                "capacity_kwh": 200,
                "initial_energy_kwh": 120,
                "minimum_energy_kwh": 40,
                "max_charge_kwh_per_hour": 50,
                "max_discharge_kwh_per_hour": 50
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 35480.0, delta=1.0)

    def test_sample_04(self):
        payload = {
            "scenario_id": "SAMPLE-04",
            "operator_notes": ["For protection testing, the battery must not discharge from 6 PM until 8 PM."],
            "hours": HOURS_S4,
            "battery": {
                "capacity_kwh": 230,
                "initial_energy_kwh": 130,
                "minimum_energy_kwh": 40,
                "max_charge_kwh_per_hour": 55,
                "max_discharge_kwh_per_hour": 55
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 40495.0, delta=1.0)

    def test_sample_05(self):
        payload = {
            "scenario_id": "SAMPLE-05",
            "operator_notes": ["From 6 PM until 9 PM, campus grid import must not exceed 155 kWh in any hour because the feeder is operating under a temporary limit."],
            "hours": HOURS_S1,
            "battery": {
                "capacity_kwh": 240,
                "initial_energy_kwh": 120,
                "minimum_energy_kwh": 30,
                "max_charge_kwh_per_hour": 60,
                "max_discharge_kwh_per_hour": 60
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 33950.0, delta=1.0)

    def test_sample_06(self):
        payload = {
            "scenario_id": "SAMPLE-06",
            "operator_notes": [
                "Cloud cover during panel inspection will leave about half of the forecast solar output from 10 AM until noon.",
                "The charging circuit will be unavailable from 2 PM until 4 PM.",
                "The library is extending book-return hours next week."
            ],
            "hours": HOURS_S6,
            "battery": {
                "capacity_kwh": 220,
                "initial_energy_kwh": 100,
                "minimum_energy_kwh": 35,
                "max_charge_kwh_per_hour": 50,
                "max_discharge_kwh_per_hour": 50
            }
        }
        resp = self.client.post('/optimize-energy', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        d = resp.json()
        self.assertAlmostEqual(d['total_cost_bdt'], 34090.0, delta=1.0)
