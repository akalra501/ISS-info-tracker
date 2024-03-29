import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from math import sqrt, atan2, degrees
import logging
from flask import Flask, jsonify
from astropy import units 
from astropy import coordinates
from astropy.coordinates import CartesianRepresentation, GCRS, ITRS, EarthLocation
from geopy.geocoders import Nominatim

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_iss_data(url: str) -> ET.Element:
    """
    Fetches ISS data from the given URL.

    Arguments:
        url: URL to fetch the ISS data.

    Returns:
        ElementTree Element containing the fetched ISS data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch ISS data: {e}")
        return None
    except ET.ParseError as e:
        logger.error(f"Failed to parse ISS data: {e}")
        return None

def parse_timestamp(timestamp: str) -> datetime:
    """
    Parses the timestamp string into a datetime object.

    Arguments:
        timestamp: String representing the timestamp.

    Returns:
        Datetime object parsed from the timestamp string.
    """
    # Remove the 'Z' character at the end
    timestamp = timestamp.rstrip('Z')
    # Parse the timestamp using the specified format
    return datetime.strptime(timestamp, "%Y-%jT%H:%M:%S.%f")

def calculate_speed(x_dot: float, y_dot: float, z_dot: float) -> float:
    """
    Calculates speed from Cartesian velocity vectors.

    Arguments:
        x_dot: Velocity component along the x-axis.
        y_dot: Velocity component along the y-axis.
        z_dot: Velocity component along the z-axis.

    Returns:
        Speed calculated from the velocity vectors.
    """
    return sqrt(x_dot**2 + y_dot**2 + z_dot**2)

def analyze_iss_data(data: ET.Element) -> list:
    """
    Analyzes ISS data.

    Arguments:
        data: ElementTree Element containing ISS data.

    Returns:
        List of stateVector elements.
    """
    if data is None:
        logger.error("No data to analyze.")
        return []

    return data.findall('.//stateVector')

@app.route('/comment', methods=['GET'], endpoint='get_comment')
def get_comment():
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    if iss_data:
        comment = [comment.text for comment in iss_data.findall('.//COMMENT')]
        return jsonify({"comment": comment})
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/header', methods=['GET'], endpoint='get_header')
def get_header():
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    if iss_data:
        header = {
            "CREATION_DATE": iss_data.find('.//CREATION_DATE').text,
            "ORIGINATOR": iss_data.find('.//ORIGINATOR').text
        }
        return jsonify({"header": header})
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/metadata', methods=['GET'], endpoint='get_metadata')
def get_metadata():
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    if iss_data:
        metadata = {elem.tag: elem.text for elem in iss_data.find('.//metadata')}
        return jsonify({"metadata": metadata})
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/epochs', methods=['GET'], endpoint='get_epochs')
def get_epochs():
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        return jsonify({"epochs": [sv.find('EPOCH').text for sv in state_vectors]})
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/epochs/<epoch>', methods=['GET'], endpoint='get_state_vectors')
def get_state_vectors(epoch: str):
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        for sv in state_vectors:
            if sv.find('EPOCH').text == epoch:
                state_vector = {
                    "X": float(sv.find('X').text),
                    "Y": float(sv.find('Y').text),
                    "Z": float(sv.find('Z').text),
                    "X_DOT": float(sv.find('X_DOT').text),
                    "Y_DOT": float(sv.find('Y_DOT').text),
                    "Z_DOT": float(sv.find('Z_DOT').text)
                }
                return jsonify({"state_vector": state_vector})
        return jsonify({"error": "Epoch not found"}), 404
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/epochs/<epoch>/speed', methods=['GET'], endpoint='get_instantaneous_speed')
def get_instantaneous_speed(epoch: str):
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        for sv in state_vectors:
            if sv.find('EPOCH').text == epoch:
                speed = calculate_speed(
                    float(sv.find('X_DOT').text),
                    float(sv.find('Y_DOT').text),
                    float(sv.find('Z_DOT').text)
                )
                return jsonify({"speed": speed})
        return jsonify({"error": "Epoch not found"}), 404
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

@app.route('/epochs/<epoch>/location', methods=['GET'])
def get_location(epoch: str):
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    if iss_data:
        for sv in iss_data.findall('.//stateVector'):
            if sv.find('EPOCH').text == epoch:
                x = float(sv.find('X').text)
                y = float(sv.find('Y').text)
                z = float(sv.find('Z').text)
                
                # Geoposition calculation
                lat = degrees(atan2(z, sqrt(x**2 + y**2)))
                
                # Extract hours and minutes from the timestamp
                timestamp = parse_timestamp(sv.find('EPOCH').text)
                hrs = timestamp.hour
                mins = timestamp.minute
                
                lon = degrees(atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 19
                # Longitude correction
                if lon > 180:
                    lon -= 360
                elif lon < -180:
                    lon += 360

                # Altitude can be negative
                altitude = float(sv.find('Z').text)

                # Reverse geocoding
                geocoder = Nominatim(user_agent='iss_tracker')
                geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')

                location = {
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": altitude,
                    "geolocation": str(geoloc)
                }
                return jsonify({"location": location})
        return jsonify({"error": "Epoch not found"}), 404
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500
        
@app.route('/now', methods=['GET'], endpoint='get_current_location')
def get_current_location():
    """
    Calculates the closest epoch to the current time and the instantaneous speed at that epoch.
    """
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        # Find the state vector closest to the current time
        current_time = datetime.utcnow()
        closest_sv = min(state_vectors, key=lambda sv: abs(parse_timestamp(sv.find('EPOCH').text) - current_time))

        x = float(closest_sv.find('X').text)
        y = float(closest_sv.find('Y').text)
        z = float(closest_sv.find('Z').text)
        speed = calculate_speed(x,y,z)
        # Geoposition calculation
        this_epoch = parse_timestamp(closest_sv.find('EPOCH').text)
        cartrep = coordinates.CartesianRepresentation([x, y, z], unit=units.km)
        gcrs = coordinates.GCRS(cartrep, obstime=this_epoch)
        itrs = gcrs.transform_to(coordinates.ITRS(obstime=this_epoch))
        loc = coordinates.EarthLocation(*itrs.cartesian.xyz)
        lat = loc.lat.value
        long = loc.lon.value
        alt = loc.height.value

        geocoder = Nominatim(user_agent='iss_tracker')
        geoloc = geocoder.reverse((lat, long), zoom=15, language='en')

        current_location = {
            'current latitude': lat,
            'current longitude': long,
            'current altitude': alt,
            'geolocation': str(geoloc),
            'instantaneous speed': speed
        }
        return jsonify({"current_location": current_location})
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
