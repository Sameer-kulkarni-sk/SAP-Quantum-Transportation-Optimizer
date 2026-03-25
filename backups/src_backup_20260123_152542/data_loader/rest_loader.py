"""REST API data loader for shipments, trucks, and lanes"""

from models.lane import Lane
from models.truck import Truck
from models.shipment import Shipment
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class RESTLoader:
    """Load transport data from REST API"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize REST loader

        Args:
            base_url: Base URL of the REST API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = 30  # seconds

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make HTTP GET request to API

        Args:
            endpoint: API endpoint (e.g., '/shipments')

        Returns:
            JSON response as dictionary, or None on error
        """
        url = f"{self.base_url}{endpoint}"

        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            request = Request(url, headers=headers)
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))

        except HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason} for {url}")
            return None
        except URLError as e:
            print(f"URL Error: {e.reason} for {url}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None

    def load_shipments(self, endpoint: str = "/shipments") -> List[Shipment]:
        """
        Load shipments from REST API

        Expected JSON format:
        {
            "shipments": [
                {
                    "shipment_id": "SH001",
                    "origin": "Berlin",
                    "destination": "Munich",
                    "weight_kg": 500.0,
                    "volume_m3": 2.5,
                    "priority": 3,
                    "deadline": "2026-01-20T18:00:00",
                    "value_eur": 5000.0
                },
                ...
            ]
        }

        Args:
            endpoint: API endpoint for shipments

        Returns:
            List of Shipment objects
        """
        data = self._make_request(endpoint)
        if not data:
            return []

        shipments = []
        shipment_list = data.get('shipments', [])

        for item in shipment_list:
            try:
                shipment = Shipment(
                    shipment_id=item['shipment_id'],
                    origin=item['origin'],
                    destination=item['destination'],
                    weight_kg=float(item['weight_kg']),
                    volume_m3=float(item['volume_m3']),
                    priority=int(item['priority']),
                    deadline=datetime.fromisoformat(item['deadline']),
                    value_eur=float(item['value_eur'])
                )
                shipments.append(shipment)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid shipment: {e}")
                continue

        print(f"Loaded {len(shipments)} shipments from API")
        return shipments

    def load_trucks(self, endpoint: str = "/trucks") -> List[Truck]:
        """
        Load trucks from REST API

        Expected JSON format:
        {
            "trucks": [
                {
                    "truck_id": "TR001",
                    "capacity_weight_kg": 1000.0,
                    "capacity_volume_m3": 5.0,
                    "cost_per_km_eur": 1.2,
                    "co2_per_km_kg": 0.8,
                    "location": "Berlin",
                    "available": true
                },
                ...
            ]
        }

        Args:
            endpoint: API endpoint for trucks

        Returns:
            List of Truck objects
        """
        data = self._make_request(endpoint)
        if not data:
            return []

        trucks = []
        truck_list = data.get('trucks', [])

        for item in truck_list:
            try:
                truck = Truck(
                    truck_id=item['truck_id'],
                    capacity_weight_kg=float(item['capacity_weight_kg']),
                    capacity_volume_m3=float(item['capacity_volume_m3']),
                    cost_per_km_eur=float(item['cost_per_km_eur']),
                    co2_per_km_kg=float(item['co2_per_km_kg']),
                    location=item['location'],
                    available=bool(item.get('available', True))
                )
                trucks.append(truck)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid truck: {e}")
                continue

        print(f"Loaded {len(trucks)} trucks from API")
        return trucks

    def load_lanes(self, endpoint: str = "/lanes") -> List[Lane]:
        """
        Load lanes from REST API

        Expected JSON format:
        {
            "lanes": [
                {
                    "lane_id": "LN001",
                    "origin": "Berlin",
                    "destination": "Munich",
                    "distance_km": 584.0,
                    "travel_time_hours": 6.5,
                    "toll_cost_eur": 45.0,
                    "traffic_factor": 1.0
                },
                ...
            ]
        }

        Args:
            endpoint: API endpoint for lanes

        Returns:
            List of Lane objects
        """
        data = self._make_request(endpoint)
        if not data:
            return []

        lanes = []
        lane_list = data.get('lanes', [])

        for item in lane_list:
            try:
                lane = Lane(
                    lane_id=item['lane_id'],
                    origin=item['origin'],
                    destination=item['destination'],
                    distance_km=float(item['distance_km']),
                    travel_time_hours=float(item['travel_time_hours']),
                    toll_cost_eur=float(item['toll_cost_eur']),
                    traffic_factor=float(item.get('traffic_factor', 1.0))
                )
                lanes.append(lane)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid lane: {e}")
                continue

        print(f"Loaded {len(lanes)} lanes from API")
        return lanes

    def load_all(self) -> Dict[str, List]:
        """
        Load all data from REST API

        Returns:
            Dictionary with 'shipments', 'trucks', and 'lanes' keys
        """
        return {
            'shipments': self.load_shipments(),
            'trucks': self.load_trucks(),
            'lanes': self.load_lanes()
        }

    def post_results(self, assignments: List[Dict],
                     endpoint: str = "/results") -> bool:
        """
        Post optimization results to API

        Args:
            assignments: List of assignment dictionaries
            endpoint: API endpoint for posting results

        Returns:
            True if successful
        """
        url = f"{self.base_url}{endpoint}"

        # Convert assignments to JSON-serializable format
        results = []
        for assignment in assignments:
            results.append({
                'shipment_id': assignment['shipment'].shipment_id,
                'truck_id': assignment['truck'].truck_id,
                'lane_id': assignment['lane'].lane_id,
                'cost_eur': assignment.get('cost', 0),
                'co2_kg': assignment.get('co2', 0)
            })

        payload = json.dumps({'results': results}).encode('utf-8')

        try:
            headers = {
                'Content-Type': 'application/json',
                'Content-Length': str(len(payload))
            }
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            request = Request(url, data=payload,
                              headers=headers, method='POST')
            with urlopen(request, timeout=self.timeout) as response:
                print(f"Results posted successfully: {response.status}")
                return True

        except Exception as e:
            print(f"Error posting results: {e}")
            return False
