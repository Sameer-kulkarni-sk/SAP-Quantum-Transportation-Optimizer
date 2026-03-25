"""CSV data loader for shipments, trucks, and lanes"""

from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class CSVLoader:
    """Load transport data from CSV files"""

    def __init__(self, data_dir: str = "data/input"):
        """
        Initialize CSV loader

        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = Path(data_dir)

    def load_shipments(self, filename: str = "shipments.csv") -> List[Shipment]:
        """
        Load shipments from CSV file

        CSV format:
        shipment_id,origin,destination,weight_kg,volume_m3,priority,deadline,value_eur

        Args:
            filename: Name of CSV file

        Returns:
            List of Shipment objects
        """
        filepath = self.data_dir / filename
        shipments = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        shipment = Shipment(
                            shipment_id=row['shipment_id'],
                            origin=row['origin'],
                            destination=row['destination'],
                            weight_kg=float(row['weight_kg']),
                            volume_m3=float(row['volume_m3']),
                            priority=int(row['priority']),
                            deadline=datetime.fromisoformat(row['deadline']),
                            value_eur=float(row['value_eur'])
                        )
                        shipments.append(shipment)
                    except (KeyError, ValueError) as e:
                        print(f"Warning: Skipping invalid shipment row: {e}")
                        continue
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error loading shipments: {e}")
            return []

        print(f"Loaded {len(shipments)} shipments from {filename}")
        return shipments

    def load_trucks(self, filename: str = "trucks.csv") -> List[Truck]:
        """
        Load trucks from CSV file

        CSV format:
        truck_id,capacity_weight_kg,capacity_volume_m3,cost_per_km_eur,co2_per_km_kg,location,available

        Args:
            filename: Name of CSV file

        Returns:
            List of Truck objects
        """
        filepath = self.data_dir / filename
        trucks = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Convert string 'true'/'false' to boolean
                        available = row.get('available', 'true').lower() in (
                            'true', '1', 'yes')

                        truck = Truck(
                            truck_id=row['truck_id'],
                            capacity_weight_kg=float(
                                row['capacity_weight_kg']),
                            capacity_volume_m3=float(
                                row['capacity_volume_m3']),
                            cost_per_km_eur=float(row['cost_per_km_eur']),
                            co2_per_km_kg=float(row['co2_per_km_kg']),
                            location=row['location'],
                            available=available
                        )
                        trucks.append(truck)
                    except (KeyError, ValueError) as e:
                        print(f"Warning: Skipping invalid truck row: {e}")
                        continue
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error loading trucks: {e}")
            return []

        print(f"Loaded {len(trucks)} trucks from {filename}")
        return trucks

    def load_lanes(self, filename: str = "lanes.csv") -> List[Lane]:
        """
        Load lanes from CSV file

        CSV format:
        lane_id,origin,destination,distance_km,travel_time_hours,toll_cost_eur,traffic_factor

        Args:
            filename: Name of CSV file

        Returns:
            List of Lane objects
        """
        filepath = self.data_dir / filename
        lanes = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        lane = Lane(
                            lane_id=row['lane_id'],
                            origin=row['origin'],
                            destination=row['destination'],
                            distance_km=float(row['distance_km']),
                            travel_time_hours=float(row['travel_time_hours']),
                            toll_cost_eur=float(row['toll_cost_eur']),
                            traffic_factor=float(
                                row.get('traffic_factor', 1.0))
                        )
                        lanes.append(lane)
                    except (KeyError, ValueError) as e:
                        print(f"Warning: Skipping invalid lane row: {e}")
                        continue
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error loading lanes: {e}")
            return []

        print(f"Loaded {len(lanes)} lanes from {filename}")
        return lanes

    def load_all(self, shipments_file: str = "shipments.csv",
                 trucks_file: str = "trucks.csv",
                 lanes_file: str = "lanes.csv") -> Dict[str, List]:
        """
        Load all data from CSV files

        Args:
            shipments_file: Shipments CSV filename
            trucks_file: Trucks CSV filename
            lanes_file: Lanes CSV filename

        Returns:
            Dictionary with 'shipments', 'trucks', and 'lanes' keys
        """
        return {
            'shipments': self.load_shipments(shipments_file),
            'trucks': self.load_trucks(trucks_file),
            'lanes': self.load_lanes(lanes_file)
        }

    def save_results(self, assignments: List[Dict[str, Any]],
                     filename: str = "results.csv") -> bool:
        """
        Save optimization results to CSV

        Args:
            assignments: List of assignment dictionaries
            filename: Output filename

        Returns:
            True if successful
        """
        filepath = self.data_dir.parent / "output" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if not assignments:
                    return True

                fieldnames = ['shipment_id', 'truck_id', 'lane_id',
                              'cost_eur', 'co2_kg', 'distance_km']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for assignment in assignments:
                    writer.writerow({
                        'shipment_id': assignment['shipment'].shipment_id,
                        'truck_id': assignment['truck'].truck_id,
                        'lane_id': assignment['lane'].lane_id,
                        'cost_eur': assignment.get('cost', 0),
                        'co2_kg': assignment.get('co2', 0),
                        'distance_km': assignment['lane'].distance_km
                    })

            print(f"Results saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
