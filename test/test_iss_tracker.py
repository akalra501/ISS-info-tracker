import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from math import isclose
import pytest
from unittest.mock import patch
from iss_tracker import app, fetch_iss_data, parse_timestamp, calculate_speed, analyze_iss_data


@pytest.fixture
def sample_iss_data():
    # Sample ISS data in XML format
    xml_data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <ndm>
        <oem id="CCSDS_OEM_VERS" version="2.0">
            <header>
                <CREATION_DATE>2024-047T18:58:31.010Z</CREATION_DATE>
                <ORIGINATOR>JSC</ORIGINATOR>
            </header>
            <body>
                <segment>
                    <metadata>
                        <OBJECT_NAME>ISS</OBJECT_NAME>
                        <OBJECT_ID>1998-067-A</OBJECT_ID>
                        <CENTER_NAME>EARTH</CENTER_NAME>
                        <REF_FRAME>EME2000</REF_FRAME>
                        <TIME_SYSTEM>UTC</TIME_SYSTEM>
                        <START_TIME>2024-047T12:00:00.000Z</START_TIME>
                        <STOP_TIME>2024-062T12:00:00.000Z</STOP_TIME>
                    </metadata>
                    <data>
                        <!-- State vectors -->
                        <stateVector>
                            <EPOCH>2024-047T12:00:00.000Z</EPOCH>
                            <X units="km">-4986.0259430215301</X>
                            <Y units="km">-3800.9118236775798</Y>
                            <Z units="km">2615.0507852302399</Z>
                            <X_DOT units="km/s">4.86633012990265</X_DOT>
                            <Y_DOT units="km/s">-2.7743207039670099</Y_DOT>
                            <Z_DOT units="km/s">5.2293448011352002</Z_DOT>
                        </stateVector>
                        <!-- More state vectors... -->
                    </data>
                </segment>
            </body>
        </oem>
    </ndm>"""
    return ET.fromstring(xml_data)

def test_fetch_iss_data(requests_mock, sample_iss_data):
    # Mocking the requests library to return sample ISS data
    requests_mock.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml", text=ET.tostring(sample_iss_data).decode("utf-8"))

    # Test fetching ISS data
    iss_data = fetch_iss_data("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml")
    assert iss_data is not None
    assert isinstance(iss_data, ET.Element)

def test_parse_timestamp():
    # Test parsing timestamp
    timestamp = "2024-047T12:00:00.000Z"
    result = parse_timestamp(timestamp)
    assert isinstance(result, datetime)
    assert result.isoformat() == "2024-02-16T12:00:00"

def test_calculate_speed():
    # Test calculating speed
    x_dot, y_dot, z_dot = 1.0, 2.0, 3.0
    speed = calculate_speed(x_dot, y_dot, z_dot)
    assert isclose(speed, 3.7416573867739413, rel_tol=1e-9)

@patch('iss_tracker.analyze_iss_data')
def test_get_epochs_with_limit_and_offset(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//stateVector')]

    # Test fetching epochs with limit and offset
    limit = 5
    offset = 2
    response = app.test_client().get(f'/epochs?limit={limit}&offset={offset}')
    assert response.status_code == 200
    assert response.json is not None


@patch('iss_tracker.analyze_iss_data')
def test_get_comment(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//COMMENT')]

    # Test fetching comment
    response = app.test_client().get('/comment')
    assert response.status_code == 200
    assert 'comment' in response.json

@patch('iss_tracker.analyze_iss_data')
def test_get_header(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//CREATION_DATE'), sample_iss_data.find('.//ORIGINATOR')]

    # Test fetching header
    response = app.test_client().get('/header')
    assert response.status_code == 200
    assert 'header' in response.json

@patch('iss_tracker.analyze_iss_data')
def test_get_metadata(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//metadata')]

    # Test fetching metadata
    response = app.test_client().get('/metadata')
    assert response.status_code == 200
    assert 'metadata' in response.json

@patch('iss_tracker.analyze_iss_data')
def test_get_epochs(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//stateVector')]

    # Test fetching epochs
    response = app.test_client().get('/epochs')
    assert response.status_code == 200
    assert 'epochs' in response.json

@patch('iss_tracker.analyze_iss_data')
def test_get_state_vectors(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//stateVector')]

    # Test fetching state vectors
    response = app.test_client().get('/epochs/2024-047T12:00:00.000Z')
    assert response.status_code == 200
    assert 'state_vector' in response.json

@patch('iss_tracker.analyze_iss_data')
def test_get_instantaneous_speed(analyze_mock, sample_iss_data):
    # Mocking the analyze_iss_data function
    analyze_mock.return_value = [sample_iss_data.find('.//stateVector')]

    # Test fetching instantaneous speed
    response = app.test_client().get('/epochs/2024-047T12:00:00.000Z/speed')
    assert response.status_code == 200
    assert 'speed' in response.json

@patch('geopy.geocoders.Nominatim.reverse')
def test_get_location(reverse_mock, sample_iss_data):
    # Test fetching location
    with patch('iss_tracker.fetch_iss_data', return_value=sample_iss_data):
        response = app.test_client().get('/epochs/2024-047T12:00:00.000Z/location')
        assert response.status_code == 200
        assert 'location' in response.json

@patch('geopy.geocoders.Nominatim.reverse')
def test_get_current_location(reverse_mock, sample_iss_data):
    # Test fetching current location
    with patch('iss_tracker.fetch_iss_data', return_value=sample_iss_data):
        response = app.test_client().get('/now')
        assert response.status_code == 200
        assert 'current_location' in response.json


if __name__ == "__main__":
    pytest.main(['-v'])
