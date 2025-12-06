"""Tests for API client."""

from unittest.mock import patch

import pytest

from rejseplanen.api import RejseplanenAPI
from rejseplanen.models import Departure, Location, Trip


def test_api_requires_key():
    """Test that API requires an API key."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = None
        with pytest.raises(ValueError, match="API key not found"):
            RejseplanenAPI()


def test_search_location(mock_api, sample_locations):
    """Test location search without addresses."""
    mock_api.search_location.return_value = sample_locations

    results = mock_api.search_location("Nørreport")

    assert len(results) == 2
    assert all(isinstance(loc, Location) for loc in results)
    assert results[0].name == "Nørreport St. (Metro)"


def test_search_location_with_addresses():
    """Test location search including addresses."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "stopLocationOrCoordLocation": [
                {
                    "StopLocation": {
                        "id": "test1",
                        "name": "Test Station",
                        "lon": 12.5,
                        "lat": 55.6
                    }
                },
                {
                    "CoordLocation": {
                        "id": "test2",
                        "name": "Test Address",
                        "type": "ADR",
                        "lon": 12.6,
                        "lat": 55.7
                    }
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.search_location("test", include_addresses=True)

            assert len(results) == 2
            assert results[0].type == "stop"
            assert results[1].type == "adr"


def test_find_nearby_stops():
    """Test finding nearby stops."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "stopLocationOrCoordLocation": [
                {
                    "StopLocation": {
                        "id": "nearby1",
                        "name": "Nearby Station",
                        "lon": 12.5,
                        "lat": 55.6,
                        "dist": 150
                    }
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.find_nearby_stops(55.6, 12.5)

            assert len(results) == 1
            assert results[0].name == "Nearby Station"
            assert hasattr(results[0], '__dict__')
            assert results[0].__dict__.get('distance') == 150


def test_get_departures():
    """Test getting departures."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "Departure": [
                {
                    "name": "A",
                    "type": "ST",
                    "stop": "Test St.",
                    "date": "2025-12-06",
                    "time": "10:30:00",
                    "direction": "Test Direction",
                    "track": "4"
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.get_departures("test_id")

            assert len(results) == 1
            assert isinstance(results[0], Departure)
            assert results[0].name == "A"
            assert results[0].track == "4"


def test_plan_trip_with_price():
    """Test trip planning with price extraction."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "Trip": [
                {
                    "LegList": {
                        "Leg": {
                            "Origin": {
                                "name": "Origin",
                                "id": "origin_id",
                                "lon": 12.5,
                                "lat": 55.6,
                                "date": "2025-12-06",
                                "time": "10:00:00"
                            },
                            "Destination": {
                                "name": "Destination",
                                "id": "dest_id",
                                "lon": 12.6,
                                "lat": 55.7,
                                "date": "2025-12-06",
                                "time": "10:30:00"
                            },
                            "name": "A",
                            "category": "006",
                            "duration": "PT30M"
                        }
                    },
                    "TariffResult": {
                        "fareSetItem": {
                            "fareItem": {
                                "price": 2400,
                                "cur": "DKK",
                                "param": [
                                    {"name": "psg", "value": "A"},
                                    {"name": "prod_name", "value": "EasyTrip"}
                                ]
                            }
                        }
                    }
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.plan_trip("origin_id", "dest_id")

            assert len(results) == 1
            assert isinstance(results[0], Trip)
            assert results[0].price == 24.0  # 2400 øre = 24 DKK
            assert results[0].currency == "DKK"
            assert results[0].fare_type == "EasyTrip"
            assert len(results[0].legs) == 1


def test_get_departures_with_realtime():
    """Test departures with real-time data."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "Departure": [
                {
                    "name": "A",
                    "type": "ST",
                    "stop": "Test St.",
                    "date": "2025-12-06",
                    "time": "10:30:00",
                    "rtDate": "2025-12-06",
                    "rtTime": "10:35:00",
                    "direction": "Test Direction",
                    "rtTrack": "5"
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.get_departures("test_id")

            assert len(results) == 1
            assert results[0].rtTime is not None
            assert results[0].is_delayed


def test_get_departures_skips_invalid():
    """Test that invalid departures are skipped."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "Departure": [
                {
                    "name": "A",
                    "type": "ST",
                    "stop": "Test St.",
                    "date": "",  # Invalid
                    "time": "10:30:00",
                },
                {
                    "name": "B",
                    "type": "ST",
                    "stop": "Test St.",
                    "date": "2025-12-06",
                    "time": "11:00:00",
                    "track": "2"
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.get_departures("test_id")

            # Only valid departure should be returned
            assert len(results) == 1
            assert results[0].name == "B"


def test_plan_trip_multiple_legs():
    """Test trip with multiple legs."""
    with patch('rejseplanen.api.Config') as mock_config:
        mock_config.return_value.get_api_key.return_value = "test_key"
        api = RejseplanenAPI()

        mock_response = {
            "Trip": [
                {
                    "LegList": {
                        "Leg": [
                            {
                                "Origin": {
                                    "name": "Start",
                                    "id": "1",
                                    "lon": 12.5,
                                    "lat": 55.6,
                                    "date": "2025-12-06",
                                    "time": "10:00:00"
                                },
                                "Destination": {
                                    "name": "Middle",
                                    "id": "2",
                                    "lon": 12.55,
                                    "lat": 55.65,
                                    "date": "2025-12-06",
                                    "time": "10:15:00"
                                },
                                "name": "A",
                                "category": "006"
                            },
                            {
                                "Origin": {
                                    "name": "Middle",
                                    "id": "2",
                                    "lon": 12.55,
                                    "lat": 55.65,
                                    "date": "2025-12-06",
                                    "time": "10:20:00"
                                },
                                "Destination": {
                                    "name": "End",
                                    "id": "3",
                                    "lon": 12.6,
                                    "lat": 55.7,
                                    "date": "2025-12-06",
                                    "time": "10:40:00"
                                },
                                "name": "B",
                                "category": "006"
                            }
                        ]
                    }
                }
            ]
        }

        with patch.object(api, '_request', return_value=mock_response):
            results = api.plan_trip("1", "3")

            assert len(results) == 1
            assert len(results[0].legs) == 2
            assert results[0].num_changes == 1
