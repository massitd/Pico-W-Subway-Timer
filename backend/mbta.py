from flask import Flask, jsonify, render_template
import requests
from datetime import datetime, timezone
from dateutil import parser
import threading
import time

app = Flask(__name__)

MBTA_API_KEY = 'd559228707644768b4cd1e5696b396db'
MBTA_URL = (
    'https://api-v3.mbta.com/predictions'
    '?filter[stop]=place-gover'    # set which stop
    '&filter[route]=Green-D'           # set which line
    '&filter[direction_id]=0'      # set direction
    '&sort=departure_time'         # sort soonest first
    '&api_key=d559228707644768b4cd1e5696b396db')

train_data_cache = {
    'next_train': None,
    'following_train': None
}


def  get_train_data_raw():
    try:
        # request to mbta API
        response = requests.get(MBTA_URL)
        response.raise_for_status()

        # parse JSON response
        mbta_data = response.json()
        departures = []

        # get current time in UTC
        now = datetime.now(timezone.utc)

        # loop over each prediction entry
        for item in mbta_data.get('data', []):
            dep_time_str = item['attributes'].get('departure_time')
            if dep_time_str:
                # parse ISO 8601 time into datetime object
                dep_time = parser.isoparse(dep_time_str)

                # calculate minutes till departure
                minutes_away = (dep_time - now).total_seconds() / 60

                # only include trains in the future
                if minutes_away >= 0:
                    departures.append({
                        'minutes_away': int(round(minutes_away)),
                        'departure_time': dep_time_str
                    })

        # return the next two trains
        return {
            'next_train': departures[0] if len(departures) > 0 else None,
            'following_train': departures[1] if len(departures) > 1 else None
        }


    except Exception as e:
        # returns error info if there's a problem
        return jsonify({'error': str(e)}), 500

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
    app.run(debug=True)