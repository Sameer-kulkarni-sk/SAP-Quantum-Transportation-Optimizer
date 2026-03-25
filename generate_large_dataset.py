#!/usr/bin/env python3
"""
Generate large test datasets for the Quantum Transport Optimizer
"""
import csv
import random
from datetime import datetime, timedelta

# German cities for realistic data
CITIES = [
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart",
    "Dusseldorf", "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden",
    "Hanover", "Nuremberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld",
    "Bonn", "Munster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden",
    "Gelsenkirchen", "Monchengladbach", "Braunschweig", "Chemnitz", "Kiel",
    "Aachen", "Halle", "Magdeburg", "Freiburg", "Krefeld", "Lubeck",
    "Oberhausen", "Erfurt", "Mainz", "Rostock", "Kassel"
]


def generate_shipments(num_shipments=1000):
    """Generate shipment data"""
    shipments = []
    base_date = datetime(2026, 1, 15)

    for i in range(1, num_shipments + 1):
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])

        shipment = {
            'shipment_id': f'SH{i:04d}',
            'origin': origin,
            'destination': destination,
            'weight_kg': random.randint(100, 1000),
            'volume_m3': round(random.uniform(0.5, 5.0), 1),
            'priority': random.randint(1, 5),
            'deadline': (base_date + timedelta(days=random.randint(1, 14))).isoformat(),
            'value_eur': random.randint(1000, 10000)
        }
        shipments.append(shipment)

    return shipments


def generate_trucks(num_trucks=200):
    """Generate truck data"""
    trucks = []

    for i in range(1, num_trucks + 1):
        truck = {
            'truck_id': f'TR{i:04d}',
            'capacity_weight_kg': random.choice([800, 1000, 1200, 1500, 2000]),
            'capacity_volume_m3': random.choice([4.0, 5.0, 6.0, 7.5, 10.0]),
            'cost_per_km_eur': round(random.uniform(0.8, 1.8), 2),
            'co2_per_km_kg': round(random.uniform(0.5, 1.2), 2),
            'location': random.choice(CITIES),
            'available': 'true'
        }
        trucks.append(truck)

    return trucks


def generate_lanes(shipments=None):
    """
    Generate lane data ensuring all shipment routes are covered

    Args:
        shipments: List of shipments to ensure lane coverage for
    """
    lanes = []
    lane_set = set()

    # First, create lanes for all shipment routes
    if shipments:
        print("Creating lanes for all shipment routes...")
        for shipment in shipments:
            lane_key = (shipment['origin'], shipment['destination'])
            if lane_key not in lane_set:
                lane_set.add(lane_key)

                # Calculate realistic distance
                distance = random.randint(100, 800)

                lane = {
                    'lane_id': f'LN{len(lanes)+1:04d}',
                    'origin': shipment['origin'],
                    'destination': shipment['destination'],
                    'distance_km': distance,
                    'travel_time_hours': round(distance / 80 + random.uniform(0.5, 2), 1),
                    'toll_cost_eur': round(distance * 0.08 + random.uniform(-5, 10), 1),
                    'traffic_factor': round(random.uniform(0.9, 1.3), 2)
                }
                lanes.append(lane)

    # Add some additional random lanes for flexibility
    additional_lanes = 200
    attempts = 0
    max_attempts = 1000

    while len(lanes) < len(lane_set) + additional_lanes and attempts < max_attempts:
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])

        lane_key = (origin, destination)
        if lane_key in lane_set:
            attempts += 1
            continue

        lane_set.add(lane_key)
        distance = random.randint(100, 800)

        lane = {
            'lane_id': f'LN{len(lanes)+1:04d}',
            'origin': origin,
            'destination': destination,
            'distance_km': distance,
            'travel_time_hours': round(distance / 80 + random.uniform(0.5, 2), 1),
            'toll_cost_eur': round(distance * 0.08 + random.uniform(-5, 10), 1),
            'traffic_factor': round(random.uniform(0.9, 1.3), 2)
        }
        lanes.append(lane)
        attempts += 1

    return lanes


def write_csv(filename, data, fieldnames):
    """Write data to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Generated {filename} with {len(data)} entries")


if __name__ == '__main__':
    print("Generating large test datasets...")
    print()

    # Generate datasets
    shipments = generate_shipments(1000)
    trucks = generate_trucks(200)
    lanes = generate_lanes(shipments)  # Pass shipments to ensure coverage

    # Write to CSV files
    write_csv('data/input/shipments.csv', shipments,
              ['shipment_id', 'origin', 'destination', 'weight_kg', 'volume_m3',
               'priority', 'deadline', 'value_eur'])

    write_csv('data/input/trucks.csv', trucks,
              ['truck_id', 'capacity_weight_kg', 'capacity_volume_m3',
               'cost_per_km_eur', 'co2_per_km_kg', 'location', 'available'])

    write_csv('data/input/lanes.csv', lanes,
              ['lane_id', 'origin', 'destination', 'distance_km',
               'travel_time_hours', 'toll_cost_eur', 'traffic_factor'])

    print()
    print("Dataset generation complete!")
    print(f"- Shipments: {len(shipments)}")
    print(f"- Trucks: {len(trucks)}")
    print(f"- Lanes: {len(lanes)}")
