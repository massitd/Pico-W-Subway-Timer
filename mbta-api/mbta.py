from flask import Flask, jsonify, render_template
import requests
from datetime import datetime, timezone
from dateutil import parser
import threading
import time

app = Flask(__name__)

MBTA_API_KEY = 'd559228707644768b4cd1e5696b396db'

MBTA_STOP = 'place-gover'  # Government Center
MBTA_ROUTES = ['Green-D', 'Green-E']  # Multiple lines at this stop

def make_url(route):
    return (
        f'https://api-v3.mbta.com/predictions'
        f'?filter[stop]={MBTA_STOP}'
        f'&filter[route]={route}'
        f'&filter[direction_id]=0'
        f'&sort=departure_time'
        f'&api_key={MBTA_API_KEY}'
    )


train_data_cache = {
    'green_d': {
        'next_train': None,
        'following_train': None
    },
    'green_e': {
        'next_train': None,
        'following_train': None
    }
}

def fetch_departures_for_route(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        mbta_data = response.json()
        now = datetime.now(timezone.utc)
        departures = []

        for item in mbta_data.get('data', []):
            dep_time_str = item['attributes'].get('departure_time')
            if dep_time_str:
                dep_time = parser.isoparse(dep_time_str)
                minutes_away = (dep_time - now).total_seconds() / 60
                if minutes_away >= 0:
                    departures.append({
                        'minutes_away': int(round(minutes_away)),
                        'departure_time': dep_time_str
                    })
        return departures

    except Exception as e:
        print("Error fetching route:", e)
        return []

def get_train_data_raw():
    green_d = fetch_departures_for_route(make_url('Green-D'))
    green_e = fetch_departures_for_route(make_url('Green-E'))

    return {
        'green_d': {
            'next_train': green_d[0] if len(green_d) > 0 else None,
            'following_train': green_d[1] if len(green_d) > 1 else None
        },
        'green_e': {
            'next_train': green_e[0] if len(green_e) > 0 else None,
            'following_train': green_e[1] if len(green_e) > 1 else None
        }
    }



@app.route("/api/times")
def get_train_times():
    try:
        data = get_train_data_raw()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# background thread uses get_train_data_raw()
def update_train_data_loop(interval_seconds=10):
    with app.app_context():
        while True:
            try:
                train_data = get_train_data_raw()
                train_data_cache.update(train_data)
                print("Train data updated")
            except Exception as e:
                print("Error updating train data:", e)
            time.sleep(interval_seconds)

# added safety check for single thread start
background_started = False

@app.before_request
def start_background_thread():
    global background_started
    if not background_started:
        thread = threading.Thread(target=update_train_data_loop, daemon=True)
        thread.start()
        background_started = True

# serves cached data quickly
@app.route('/api/train-times')
def api_train_times():
    return jsonify(train_data_cache)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)