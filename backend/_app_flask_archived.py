import json
import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ============================================================
# KREDENSIAL KEDUA API (Berdampingan)
# ============================================================
FOOTBALL_DATA_ORG_TOKEN = "902947a711c14897a9791bbf544299d9"
RAPIDAPI_KEY = "69d9f0a1afmshea1d32ceebf81cap10f373jsnade8f2c1b3ff"

HEADERS_RAPIDAPI = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# ============================================================
# MOCK DATA (original, unchanged)
# ============================================================
WORLD_CUP_DATA = {
    "inggris": {
        "nama_tim": "Inggris",
        "grup": "Grup C",
        "logo": "\U0001f1ec\U0001f1e7",
        "tren_performa": ["M", "M", "S", "K", "M"],
        "statistik_5_laga": {
            "gol_dicetak": 12,
            "gol_kemalingan": 4,
            "rata_penguasaan_bola": 62,
            "total_shots_on_target": 34,
            "clean_sheets": 3,
            "pelanggaran": 42,
            "kartu_kuning": 5,
            "kartu_merah": 0
        },
        "riwayat_pertandingan": [
            {"tanggal": "28 Jun 2026", "lawan": "Amerika Serikat", "skor": "3 - 1", "status": "M", "posisi": "Home"},
            {"tanggal": "23 Jun 2026", "lawan": "Aljazair", "skor": "2 - 0", "status": "M", "posisi": "Home"},
            {"tanggal": "18 Jun 2026", "lawan": "Slovenia", "skor": "1 - 1", "status": "S", "posisi": "Away"},
            {"tanggal": "12 Jun 2026", "lawan": "Prancis", "skor": "1 - 2", "status": "K", "posisi": "Away"},
            {"tanggal": "07 Jun 2026", "lawan": "Skotlandia", "skor": "5 - 0", "status": "M", "posisi": "Home"}
        ]
    },
    "perancis": {
        "nama_tim": "Prancis",
        "grup": "Grup D",
        "logo": "\U0001f1eb\U0001f1f7",
        "tren_performa": ["M", "M", "M", "S", "M"],
        "statistik_5_laga": {
            "gol_dicetak": 14,
            "gol_kemalingan": 2,
            "rata_penguasaan_bola": 58,
            "total_shots_on_target": 41,
            "clean_sheets": 4,
            "pelanggaran": 48,
            "kartu_kuning": 7,
            "kartu_merah": 1
        },
        "riwayat_pertandingan": [
            {"tanggal": "29 Jun 2026", "lawan": "Polandia", "skor": "4 - 0", "status": "M", "posisi": "Home"},
            {"tanggal": "24 Jun 2026", "lawan": "Belanda", "skor": "2 - 1", "status": "M", "posisi": "Away"},
            {"tanggal": "19 Jun 2026", "lawan": "Austria", "skor": "3 - 0", "status": "M", "posisi": "Home"},
            {"tanggal": "13 Jun 2026", "lawan": "Jerman", "skor": "0 - 0", "status": "S", "posisi": "Away"},
            {"tanggal": "08 Jun 2026", "lawan": "Inggris", "skor": "2 - 1", "status": "M", "posisi": "Home"}
        ]
    },
    "argentina": {
        "nama_tim": "Argentina",
        "grup": "Grup A",
        "logo": "\U0001f1e6\U0001f1f7",
        "tren_performa": ["K", "M", "S", "M", "M"],
        "statistik_5_laga": {
            "gol_dicetak": 9,
            "gol_kemalingan": 6,
            "rata_penguasaan_bola": 65,
            "total_shots_on_target": 38,
            "clean_sheets": 2,
            "pelanggaran": 55,
            "kartu_kuning": 12,
            "kartu_merah": 0
        },
        "riwayat_pertandingan": [
            {"tanggal": "27 Jun 2026", "lawan": "Arab Saudi", "skor": "1 - 2", "status": "K", "posisi": "Home"},
            {"tanggal": "22 Jun 2026", "lawan": "Meksiko", "skor": "2 - 0", "status": "M", "posisi": "Away"},
            {"tanggal": "17 Jun 2026", "lawan": "Polandia", "skor": "2 - 2", "status": "S", "posisi": "Home"},
            {"tanggal": "11 Jun 2026", "lawan": "Australia", "skor": "2 - 1", "status": "M", "posisi": "Away"},
            {"tanggal": "06 Jun 2026", "lawan": "Kroasia", "skor": "2 - 1", "status": "M", "posisi": "Home"}
        ]
    }
}

# ============================================================
# DATA DARI FOOTBALL-DATA.ORG
# ============================================================
FLAG_MAP = {
    "Argentina": "\U0001f1e6\U0001f1f7", "Australia": "\U0001f1e6\U0001f1fa", "Austria": "\U0001f1e6\U0001f1f9",
    "Belgium": "\U0001f1e7\U0001f1ea", "Brazil": "\U0001f1e7\U0001f1f7", "Canada": "\U0001f1e8\U0001f1e6",
    "Colombia": "\U0001f1e8\U0001f1f4", "Croatia": "\U0001f1ed\U0001f1f7", "Czechia": "\U0001f1e8\U0001f1ff",
    "Ecuador": "\U0001f1ea\U0001f1e8", "Egypt": "\U0001f1ea\U0001f1ec", "England": "\U0001f1ec\U0001f1e7",
    "France": "\U0001f1eb\U0001f1f7", "Germany": "\U0001f1e9\U0001f1ea", "Ghana": "\U0001f1ec\U0001f1ed",
    "Iran": "\U0001f1ee\U0001f1f7", "Iraq": "\U0001f1ee\U0001f1f6", "Ivory Coast": "\U0001f1e8\U0001f1ee",
    "Japan": "\U0001f1ef\U0001f1f5", "Jordan": "\U0001f1ef\U0001f1f4", "Mexico": "\U0001f1f2\U0001f1fd",
    "Morocco": "\U0001f1f2\U0001f1e6", "Netherlands": "\U0001f1f3\U0001f1f1", "New Zealand": "\U0001f1f3\U0001f1ff",
    "Norway": "\U0001f1f3\U0001f1f4", "Panama": "\U0001f1f5\U0001f1e6", "Paraguay": "\U0001f1f5\U0001f1fe",
    "Portugal": "\U0001f1f5\U0001f1f9", "Qatar": "\U0001f1f6\U0001f1e6", "Saudi Arabia": "\U0001f1f8\U0001f1e6",
    "Scotland": "\U0001f1f8\U0001f1f3", "Senegal": "\U0001f1f8\U0001f1f3",
    "South Africa": "\U0001f1ff\U0001f1e6", "South Korea": "\U0001f1f0\U0001f1f7",
    "Spain": "\U0001f1ea\U0001f1f8", "Sweden": "\U0001f1f8\U0001f1ea", "Switzerland": "\U0001f1e8\U0001f1ed",
    "Tunisia": "\U0001f1f9\U0001f1f3", "Turkey": "\U0001f1f9\U0001f1f7",
    "United States": "\U0001f1fa\U0001f1f8", "Uruguay": "\U0001f1fa\U0001f1fe",
    "Uzbekistan": "\U0001f1fa\U0001f1ff",
    "Bosnia-Herzegovina": "\U0001f1e7\U0001f1e6", "Cape Verde Islands": "\U0001f1e8\U0001f1fb",
    "Congo DR": "\U0001f1e8\U0001f1e9", "Curacao": "\U0001f1e8\U0001f1fc",
    "Haiti": "\U0001f1ed\U0001f1f9", "Algeria": "\U0001f1e9\U0001f1ff"
}

real_wc_path = os.path.join(os.path.dirname(__file__), 'real_wc_data.json')
if os.path.exists(real_wc_path):
    with open(real_wc_path) as f:
        REAL_WORLD_CUP_DATA = json.load(f)
    for name, data in REAL_WORLD_CUP_DATA.items():
        if not data.get('logo') and name in FLAG_MAP:
            data['logo'] = FLAG_MAP[name]
else:
    REAL_WORLD_CUP_DATA = {}

# ============================================================
# FUNGSI SOFASCORE / RAPIDAPI (API-FOOTBALL)
# ============================================================
TEAM_NAME_TO_FOOTBALL_API_ID = {
    "England": 10, "Argentina": 26, "France": 16, "Spain": 9,
    "Germany": 25, "Italy": 27, "Netherlands": 14, "Portugal": 30,
    "Belgium": 18, "Brazil": 12, "Mexico": 5, "Uruguay": 32,
    "Croatia": 22, "Colombia": 33, "Japan": 54, "South Korea": 55,
    "United States": 5548, "Switzerland": 23, "Senegal": 222,
    "Iran": 35, "Morocco": 53, "Serbia": 28, "Poland": 205,
    "Australia": 14, "Denmark": 21, "Tunisia": 62,
    "Costa Rica": 67, "Cameroon": 106, "Ghana": 89,
    "Saudi Arabia": 42, "Ecuador": 39, "Qatar": 73,
    "Canada": 73, "Wales": 15, "Scotland": 59, "Sweden": 20,
    "Norway": 19, "Turkey": 47, "Czechia": 49, "Austria": 81,
    "Hungary": 38, "Greece": 45, "Russia": 31, "Ukraine": 51,
    "Paraguay": 43, "South Africa": 133, "Algeria": 97,
    "Egypt": 98, "Ivory Coast": 99, "Nigeria": 101,
    "Cape Verde Islands": 117, "Panama": 68, "New Zealand": 85,
    "Uzbekistan": 86, "Iraq": 63, "Jordan": 64,
    "Bosnia-Herzegovina": 162, "Congo DR": 107, "Haiti": 79,
    "Curacao": 3898, "Slovenia": 343,
}

_rapidapi_available = None

def _check_rapidapi():
    global _rapidapi_available
    if _rapidapi_available is None:
        try:
            r = requests.get(
                "https://api-football-v1.p.rapidapi.com/v3/status",
                headers=HEADERS_RAPIDAPI, timeout=5
            )
            _rapidapi_available = (r.status_code == 200)
        except Exception:
            _rapidapi_available = False
    return _rapidapi_available

AMBIL_RAPIDAPI = os.getenv("AMBIL_RAPIDAPI", "1") == "1"

def ambil_riwayat_api_football(team_name):
    if not AMBIL_RAPIDAPI or not _check_rapidapi():
        return []

    team_id = TEAM_NAME_TO_FOOTBALL_API_ID.get(team_name)
    if not team_id:
        return []

    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {"team": team_id, "last": "5", "status": "FT"}
        resp = requests.get(url, headers=HEADERS_RAPIDAPI, params=params, timeout=8)
        if resp.status_code != 200:
            return []

        data = resp.json()
        laga_list = []
        for item in data.get("response", []):
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            fixture = item.get("fixture", {})

            home = teams.get("home", {}).get("name", "?")
            away = teams.get("away", {}).get("name", "?")
            skor_home = goals.get("home", "?")
            skor_away = goals.get("away", "?")

            status_laga = "M"
            if skor_home != "?" and skor_away != "?":
                is_home = (team_name.lower() in home.lower())
                if skor_home == skor_away:
                    status_laga = "S"
                elif (is_home and skor_home > skor_away) or (not is_home and skor_away > skor_home):
                    status_laga = "M"
                else:
                    status_laga = "K"

            laga_list.append({
                "tanggal": (fixture.get("date") or "")[:10],
                "home": home,
                "away": away,
                "skor": f"{skor_home} - {skor_away}",
                "status": status_laga
            })

        return laga_list
    except Exception:
        return []


def ambil_statistik_api_football(team_name):
    if not AMBIL_RAPIDAPI or not _check_rapidapi():
        return {}

    team_id = TEAM_NAME_TO_FOOTBALL_API_ID.get(team_name)
    if not team_id:
        return {}

    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
        params = {"team": team_id, "season": "2026", "league": 1}
        resp = requests.get(url, headers=HEADERS_RAPIDAPI, params=params, timeout=8)
        if resp.status_code != 200:
            return {}

        data = resp.json()
        response = data.get("response", {})
        if not response:
            return {}

        fixtures_data = response.get("fixtures", {})
        goals_data = response.get("goals", {})
        clean_sheet_data = response.get("clean_sheet", {})
        form = response.get("form", "")

        return {
            "played": fixtures_data.get("played", {}).get("total", 0),
            "wins": fixtures_data.get("wins", {}).get("total", 0),
            "draws": fixtures_data.get("draws", {}).get("total", 0),
            "loses": fixtures_data.get("loses", {}).get("total", 0),
            "goals_for": goals_data.get("for", {}).get("total", {}).get("total", 0),
            "goals_against": goals_data.get("against", {}).get("total", {}).get("total", 0),
            "clean_sheets": clean_sheet_data.get("total", 0),
            "form": list(form) if form else [],
        }
    except Exception:
        return {}

# ============================================================
# GABUNGKAN DATA DARI SEMUA SUMBER
# ============================================================
def build_dashboard_data():
    merged = {}

    # Masukkan mock data dulu
    for key, tim in WORLD_CUP_DATA.items():
        merged[key] = dict(tim)
        merged[key]["_sumber"] = "mock"

    # Masukkan real data dari football-data.org
    for nama, tim in REAL_WORLD_CUP_DATA.items():
        key = nama.lower().replace(" ", "_")
        if key not in merged or merged[key].get("_sumber") != "mock":
            merged[key] = dict(tim)
            merged[key]["_sumber"] = "football-data.org"
            merged[key]["riwayat_rapidapi"] = []
            merged[key]["statistik_rapidapi"] = {}

    # Coba ambil data dari API-Football untuk tim-tim yang dikenal
    for key, tim in merged.items():
        nama_asli = tim.get("nama_tim", "")
        riwayat = ambil_riwayat_api_football(nama_asli)
        if riwayat:
            tim["riwayat_rapidapi"] = riwayat
            tim["_sumber"] = "rapidapi"

        statistik = ambil_statistik_api_football(nama_asli)
        if statistik:
            tim["statistik_rapidapi"] = statistik

    return merged

@app.route("/")
def index():
    dashboard_data = build_dashboard_data()
    return render_template("index.html", data_tim=WORLD_CUP_DATA, data_real=REAL_WORLD_CUP_DATA, dashboard=dashboard_data)

@app.route("/api/tim/<id_tim>")
def get_api_tim(id_tim):
    tim = WORLD_CUP_DATA.get(id_tim.lower())
    if tim:
        return jsonify(tim)
    return jsonify({"error": "Tim tidak ditemukan"}), 404

@app.route("/api/real/tim/<nama_tim>")
def get_real_tim(nama_tim):
    tim = REAL_WORLD_CUP_DATA.get(nama_tim.title())
    if tim:
        return jsonify(tim)
    return jsonify({"error": "Tim tidak ditemukan"}), 404

@app.route("/api/real/all")
def get_real_all():
    return jsonify(REAL_WORLD_CUP_DATA)

@app.route("/api/real/groups")
def get_real_groups():
    groups = {}
    for name, data in REAL_WORLD_CUP_DATA.items():
        g = data["grup"]
        groups.setdefault(g, []).append({**data, "key": name.lower().replace(" ", "_")})
    return jsonify(groups)

@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(build_dashboard_data())

if __name__ == "__main__":
    app.run(debug=True)
