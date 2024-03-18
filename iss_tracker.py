import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from math import sqrt, atan2, degrees
import logging
from flask import Flask, jsonify

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

@app.route('/epochs/<epoch>/location', methods=['GET'], endpoint='get_location')
def get_location(epoch: str):
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        for sv in state_vectors:
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

                location = {
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": z,
                }
                return jsonify({"location": location})
        return jsonify({"error": "Epoch not found"}), 404
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500
        
@app.route('/now', methods=['GET'], endpoint='get_current_location')
def get_nearest_epoch():
    ISS_DATA_URL = "https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml"
    iss_data = fetch_iss_data(ISS_DATA_URL)
    state_vectors = analyze_iss_data(iss_data)
    if state_vectors:
        now = datetime.now()
        closest_epoch = min(state_vectors, key=lambda x: abs(now - parse_timestamp(x.find('EPOCH').text)))
        speed = calculate_speed(
            float(closest_epoch.find('X_DOT').text),
            float(closest_epoch.find('Y_DOT').text),
            float(closest_epoch.find('Z_DOT').text)
        )
        return jsonify({
            "epoch": closest_epoch.find('EPOCH').text,
            "speed": speed
        })
    else:
        return jsonify({"error": "Failed to fetch or analyze data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
