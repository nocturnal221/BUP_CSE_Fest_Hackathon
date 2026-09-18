export const PRESET_SCENARIOS = [
  {
    id: "SAMPLE-01",
    name: "Scenario 01: Solar Panel Cleaning",
    description: "Facilities wash solar panels from noon to 2 PM (25% solar). Contains a sports distractor note.",
    operator_notes: [
      "Facilities will wash the rooftop solar panels from noon until 2 PM. During cleaning, usable solar should be treated as roughly 25% of the forecast.",
      "The sports office moved next month's registration deadline."
    ],
    battery: {
      capacity_kwh: 220.0,
      initial_energy_kwh: 110.0,
      minimum_energy_kwh: 40.0,
      max_charge_kwh_per_hour: 50.0,
      max_discharge_kwh_per_hour: 50.0
    },
    hours: [
      { hour: 0, demand_kwh: 90.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 1, demand_kwh: 85.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 2, demand_kwh: 80.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 3, demand_kwh: 80.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 4, demand_kwh: 85.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 5, demand_kwh: 95.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 6, demand_kwh: 110.0, solar_kwh: 5.0, tariff_bdt_per_kwh: 8.0 },
      { hour: 7, demand_kwh: 130.0, solar_kwh: 20.0, tariff_bdt_per_kwh: 10.0 },
      { hour: 8, demand_kwh: 150.0, solar_kwh: 50.0, tariff_bdt_per_kwh: 12.0 },
      { hour: 9, demand_kwh: 165.0, solar_kwh: 90.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 10, demand_kwh: 175.0, solar_kwh: 130.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 11, demand_kwh: 180.0, solar_kwh: 160.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 12, demand_kwh: 185.0, solar_kwh: 180.0, tariff_bdt_per_kwh: 15.0 },
      { hour: 13, demand_kwh: 180.0, solar_kwh: 170.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 14, demand_kwh: 170.0, solar_kwh: 140.0, tariff_bdt_per_kwh: 13.0 },
      { hour: 15, demand_kwh: 165.0, solar_kwh: 90.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 16, demand_kwh: 170.0, solar_kwh: 45.0, tariff_bdt_per_kwh: 18.0 },
      { hour: 17, demand_kwh: 185.0, solar_kwh: 10.0, tariff_bdt_per_kwh: 22.0 },
      { hour: 18, demand_kwh: 205.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 28.0 },
      { hour: 19, demand_kwh: 215.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 30.0 },
      { hour: 20, demand_kwh: 205.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 26.0 },
      { hour: 21, demand_kwh: 175.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 18.0 },
      { hour: 22, demand_kwh: 135.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 10.0 },
      { hour: 23, demand_kwh: 105.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 7.0 }
    ]
  },
  {
    id: "SAMPLE-02",
    name: "Scenario 02: Feeder Substation Cap",
    description: "Grid import capped at 90 kWh from 6 PM to 9 PM due to feeder maintenance.",
    operator_notes: [
      "Substation feeder maintenance requires grid import capped at 90 kWh from 6 PM until 9 PM."
    ],
    battery: {
      capacity_kwh: 220.0,
      initial_energy_kwh: 110.0,
      minimum_energy_kwh: 40.0,
      max_charge_kwh_per_hour: 50.0,
      max_discharge_kwh_per_hour: 50.0
    },
    hours: [
      { hour: 0, demand_kwh: 100.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 1, demand_kwh: 95.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 2, demand_kwh: 90.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 4.0 },
      { hour: 3, demand_kwh: 90.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 4.0 },
      { hour: 4, demand_kwh: 95.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 4.0 },
      { hour: 5, demand_kwh: 105.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 6, demand_kwh: 120.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 7.0 },
      { hour: 7, demand_kwh: 135.0, solar_kwh: 10.0, tariff_bdt_per_kwh: 9.0 },
      { hour: 8, demand_kwh: 145.0, solar_kwh: 30.0, tariff_bdt_per_kwh: 11.0 },
      { hour: 9, demand_kwh: 155.0, solar_kwh: 55.0, tariff_bdt_per_kwh: 13.0 },
      { hour: 10, demand_kwh: 165.0, solar_kwh: 80.0, tariff_bdt_per_kwh: 15.0 },
      { hour: 11, demand_kwh: 175.0, solar_kwh: 100.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 12, demand_kwh: 180.0, solar_kwh: 110.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 13, demand_kwh: 175.0, solar_kwh: 105.0, tariff_bdt_per_kwh: 15.0 },
      { hour: 14, demand_kwh: 165.0, solar_kwh: 85.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 15, demand_kwh: 160.0, solar_kwh: 60.0, tariff_bdt_per_kwh: 15.0 },
      { hour: 16, demand_kwh: 170.0, solar_kwh: 30.0, tariff_bdt_per_kwh: 19.0 },
      { hour: 17, demand_kwh: 190.0, solar_kwh: 10.0, tariff_bdt_per_kwh: 24.0 },
      { hour: 18, demand_kwh: 210.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 31.0 },
      { hour: 19, demand_kwh: 220.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 33.0 },
      { hour: 20, demand_kwh: 210.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 29.0 },
      { hour: 21, demand_kwh: 180.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 20.0 },
      { hour: 22, demand_kwh: 145.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 11.0 },
      { hour: 23, demand_kwh: 115.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 7.0 }
    ]
  },
  {
    id: "SAMPLE-03",
    name: "Scenario 03: Storm Emergency Reserve",
    description: "Severe weather protocol: reserve at least 60% of battery capacity from 6 PM until 10 PM.",
    operator_notes: [
      "Severe weather alert: maintain at least 60% of battery capacity from 6 PM until 10 PM for critical clinic backup."
    ],
    battery: {
      capacity_kwh: 220.0,
      initial_energy_kwh: 110.0,
      minimum_energy_kwh: 40.0,
      max_charge_kwh_per_hour: 50.0,
      max_discharge_kwh_per_hour: 50.0
    },
    hours: [
      { hour: 0, demand_kwh: 90.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 1, demand_kwh: 85.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 2, demand_kwh: 80.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 3, demand_kwh: 80.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 4, demand_kwh: 85.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 5.0 },
      { hour: 5, demand_kwh: 95.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 6.0 },
      { hour: 6, demand_kwh: 110.0, solar_kwh: 5.0, tariff_bdt_per_kwh: 8.0 },
      { hour: 7, demand_kwh: 130.0, solar_kwh: 20.0, tariff_bdt_per_kwh: 10.0 },
      { hour: 8, demand_kwh: 150.0, solar_kwh: 50.0, tariff_bdt_per_kwh: 12.0 },
      { hour: 9, demand_kwh: 165.0, solar_kwh: 90.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 10, demand_kwh: 175.0, solar_kwh: 130.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 11, demand_kwh: 180.0, solar_kwh: 160.0, tariff_bdt_per_kwh: 16.0 },
      { hour: 12, demand_kwh: 185.0, solar_kwh: 180.0, tariff_bdt_per_kwh: 15.0 },
      { hour: 13, demand_kwh: 180.0, solar_kwh: 170.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 14, demand_kwh: 170.0, solar_kwh: 140.0, tariff_bdt_per_kwh: 13.0 },
      { hour: 15, demand_kwh: 165.0, solar_kwh: 90.0, tariff_bdt_per_kwh: 14.0 },
      { hour: 16, demand_kwh: 170.0, solar_kwh: 45.0, tariff_bdt_per_kwh: 18.0 },
      { hour: 17, demand_kwh: 185.0, solar_kwh: 10.0, tariff_bdt_per_kwh: 22.0 },
      { hour: 18, demand_kwh: 205.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 28.0 },
      { hour: 19, demand_kwh: 215.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 30.0 },
      { hour: 20, demand_kwh: 205.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 26.0 },
      { hour: 21, demand_kwh: 175.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 18.0 },
      { hour: 22, demand_kwh: 135.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 10.0 },
      { hour: 23, demand_kwh: 105.0, solar_kwh: 0.0, tariff_bdt_per_kwh: 7.0 }
    ]
  }
];
