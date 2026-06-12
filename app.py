from flask import Flask, render_template, jsonify, send_file
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='.', static_folder='static')

API_KEY = os.getenv("API_KEY")
CRICAPI_URL = "https://api.cricapi.com/v1/cricScore"

CACHE_TIME = 900
cached_live_scores = None
last_fetch_time = 0


@app.route('/')
def index():
    return render_template('cricket.html')


@app.route('/data/<filename>')
def get_data_file(filename):
    if filename not in ['players.csv', 'teams.csv']:
        return jsonify({"error": "File not found"}), 404

    filepath = os.path.join('data', filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    return send_file(filepath, mimetype='text/csv')


@app.route('/api/live-scores')
def get_live_scores():
    global cached_live_scores, last_fetch_time

    current_time = time.time()

    if cached_live_scores and current_time - last_fetch_time < CACHE_TIME:
        cached_live_scores["cached"] = True
        return jsonify(cached_live_scores)

    try:
        params = {
            "apikey": API_KEY
        }

        response = requests.get(
            CRICAPI_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        result = {
            "success": True,
            "data": data.get("data", []),
            "count": len(data.get("data", [])),
            "source": "CricAPI Real Data",
            "cached": False
        }

        cached_live_scores = result
        last_fetch_time = current_time

        return jsonify(result)

    except Exception as e:
        print("API Request Error:", str(e))

        if cached_live_scores:
            cached_live_scores["cached"] = True
            cached_live_scores["source"] = "Old Cached Data"
            return jsonify(cached_live_scores)

        sample_data = {
            "success": True,
            "data": [
                {
                    "id": "1",
                    "name": "India vs Australia",
                    "status": "Live",
                    "score": "250/3",
                    "real_data": False
                }
            ],
            "count": 1,
            "source": "Sample Data",
            "cached": False
        }

        return jsonify(sample_data)


@app.route('/api/match/<match_id>')
def get_match_details(match_id):
    return jsonify({
        "success": False,
        "message": "Match details disabled to save API requests"
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)@app.route('/api/live-scores')
def get_live_scores():
    global cached_live_scores, last_fetch_time

    current_time = time.time()

    if cached_live_scores and current_time - last_fetch_time < CACHE_TIME:
        cached_live_scores["cached"] = True
        return jsonify(cached_live_scores)

    try:
        response = requests.get(
    f"{CRICAPI_URL}?apikey={API_KEY}",
    timeout=10
    )
        
        print("API KEY LOADED:", bool(API_KEY))
        print("STATUS CODE:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        response.raise_for_status()
        api_data = response.json()

        matches = []

        for match in api_data.get("data", []):
            match_name = match.get("name", "")

            team1 = match.get("t1")
            team2 = match.get("t2")

            if not team1 or not team2:
                if " vs " in match_name:
                    parts = match_name.split(" vs ")
                    team1 = parts[0].strip()
                    team2 = parts[1].strip()
                else:
                    team1 = "Unknown Team"
                    team2 = "Unknown Team"

            matches.append({
                "id": match.get("id"),
                "name": f"{team1} vs {team2}",
                "team1": team1,
                "team2": team2,
                "team1Score": match.get("t1s") or "Yet to bat",
                "team2Score": match.get("t2s") or "Yet to bat",
                "status": match.get("status") or "Scheduled",
                "series": match.get("series") or "",
                "ms": match.get("ms") or "fixture",
                "matchType": match.get("matchType") or "",
                "dateTimeGMT": match.get("dateTimeGMT") or "",
                "real_data": True
            })

        result = {
            "success": True,
            "data": matches,
            "count": len(matches),
            "source": "CricAPI Real Data",
            "cached": False
        }

        cached_live_scores = result
        last_fetch_time = current_time

        return jsonify(result)

    except Exception as e:
        print("API Request Error:", str(e))

        if cached_live_scores:
            cached_live_scores["cached"] = True
            cached_live_scores["source"] = "Old Cached Data"
            return jsonify(cached_live_scores)

        return jsonify({
            "success": True,
            "data": [],
            "count": 0,
            "source": "No Data Available",
            "cached": False
        })