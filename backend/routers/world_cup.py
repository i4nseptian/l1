"""World Cup 2026 — mock data, football-data.org, dan RapidAPI integration."""
import os
import json
import requests
from fastapi import APIRouter
from httpx import AsyncClient

router = APIRouter(prefix='/api')

# ============================================================
# MOCK DATA (3 tim contoh)
# ============================================================
WORLD_CUP_DATA = {
    "inggris": {
        "nama_tim": "Inggris",
        "grup": "Grup C",
        "logo": "\U0001f1ec\U0001f1e7",
        "tren_performa": ["M", "M", "S", "K", "M"],
        "statistik_5_laga": {
            "gol_dicetak": 12, "gol_kemalingan": 4, "rata_penguasaan_bola": 62,
            "total_shots_on_target": 34, "clean_sheets": 3, "pelanggaran": 42,
            "kartu_kuning": 5, "kartu_merah": 0
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
            "gol_dicetak": 14, "gol_kemalingan": 2, "rata_penguasaan_bola": 58,
            "total_shots_on_target": 41, "clean_sheets": 4, "pelanggaran": 48,
            "kartu_kuning": 7, "kartu_merah": 1
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
            "gol_dicetak": 9, "gol_kemalingan": 6, "rata_penguasaan_bola": 65,
            "total_shots_on_target": 38, "clean_sheets": 2, "pelanggaran": 55,
            "kartu_kuning": 12, "kartu_merah": 0
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
# FLAG MAP & REAL DATA
# ============================================================
FLAG_MAP = {
    "Argentina": "\U0001f1e6\U0001f1f7", "Australia": "\U0001f1e6\U0001f1fa", "Austria": "\U0001f1e6\U0001f1f9",
    "Belgium": "\U0001f1e7\U0001f1ea", "Brazil": "\U0001f1e7\U0001f1f7", "Canada": "\U0001f1e8\U0001f1e6",
    "Colombia": "\U0001f1e8\U0001f1f4", "Croatia": "\U0001f1ed\U0001f1f7",     "Czechia": "\U0001f1e8\U0001f1ff",
    "Ecuador": "\U0001f1ea\U0001f1e8", "Egypt": "\U0001f1ea\U0001f1ec", "England": "\U0001f1ec\U0001f1e7",
    "France": "\U0001f1eb\U0001f1f7", "Germany": "\U0001f1e9\U0001f1ea", "Ghana": "\U0001f1ec\U0001f1ed",
    "Iran": "\U0001f1ee\U0001f1f7", "Iraq": "\U0001f1ee\U0001f1f6", "Ivory Coast": "\U0001f1e8\U0001f1ee",
    "Japan": "\U0001f1ef\U0001f1f5", "Jordan": "\U0001f1ef\U0001f1f4", "Mexico": "\U0001f1f2\U0001f1fd",
    "Morocco": "\U0001f1f2\U0001f1e6", "Netherlands": "\U0001f1f3\U0001f1f1",     "New Zealand": "\U0001f1f3\U0001f1ff",
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

real_wc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'real_wc_data.json')
if os.path.exists(real_wc_path):
    with open(real_wc_path, encoding='utf-8') as f:
        REAL_WORLD_CUP_DATA = json.load(f)
    for name, data in REAL_WORLD_CUP_DATA.items():
        if not data.get('logo') and name in FLAG_MAP:
            data['logo'] = FLAG_MAP[name]
else:
    REAL_WORLD_CUP_DATA = {}

# ============================================================
# RAPIDAPI / API-FOOTBALL
# ============================================================
RAPIDAPI_KEY = "69d9f0a1afmshea1d32ceebf81cap10f373jsnade8f2c1b3ff"
HEADERS_RAPIDAPI = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

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
                "home": home, "away": away,
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
        return {
            "played": response.get("fixtures", {}).get("played", {}).get("total", 0),
            "wins": response.get("fixtures", {}).get("wins", {}).get("total", 0),
            "draws": response.get("fixtures", {}).get("draws", {}).get("total", 0),
            "loses": response.get("fixtures", {}).get("loses", {}).get("total", 0),
            "goals_for": response.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
            "goals_against": response.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
            "clean_sheets": response.get("clean_sheet", {}).get("total", 0),
            "form": list(response.get("form", "")) if response.get("form") else [],
        }
    except Exception:
        return {}


def build_dashboard_data():
    merged = {}
    for key, tim in WORLD_CUP_DATA.items():
        merged[key] = dict(tim)
        merged[key]["_sumber"] = "mock"
    for nama, tim in REAL_WORLD_CUP_DATA.items():
        key = nama.lower().replace(" ", "_")
        if key not in merged or merged[key].get("_sumber") != "mock":
            merged[key] = dict(tim)
            merged[key]["_sumber"] = "football-data.org"
            merged[key]["riwayat_rapidapi"] = []
            merged[key]["statistik_rapidapi"] = {}
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


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/tim/{id_tim}")
async def get_tim(id_tim: str):
    tim = WORLD_CUP_DATA.get(id_tim.lower())
    if tim:
        return tim
    return {"error": "Tim tidak ditemukan"}

@router.get("/real/tim/{nama_tim}")
async def get_real_tim(nama_tim: str):
    tim = REAL_WORLD_CUP_DATA.get(nama_tim.title())
    if tim:
        return tim
    return {"error": "Tim tidak ditemukan"}

@router.get("/real/all")
async def get_real_all():
    return REAL_WORLD_CUP_DATA

@router.get("/real/groups")
async def get_real_groups():
    groups = {}
    for name, data in REAL_WORLD_CUP_DATA.items():
        g = data["grup"]
        groups.setdefault(g, []).append({**data, "key": name.lower().replace(" ", "_")})
    return groups

@router.get("/dashboard")
async def api_dashboard():
    return build_dashboard_data()


def _team_strength(tim):
    s = tim.get("statistik_5_laga", {})
    form = tim.get("tren_performa", [])
    form_score = sum({"M": 3, "S": 1, "K": 0}.get(f, 1) for f in form) / max(len(form), 1) * 10
    goal_diff = s.get("gol_dicetak", 0) - s.get("gol_kemalingan", 0)
    attack = s.get("gol_dicetak", 0) / max(len(form), 1) * 5
    defense = s.get("clean_sheets", 0) / max(len(form), 1) * 10
    return round(form_score + goal_diff * 2 + attack + defense, 1)


@router.get("/world-cup/predictions")
async def world_cup_predictions():
    groups = {}
    for name, tim in REAL_WORLD_CUP_DATA.items():
        g = tim["grup"]
        groups.setdefault(g, []).append({
            "nama": tim["nama_tim"],
            "grup": g,
            "logo": tim.get("logo", ""),
            "form": tim.get("tren_performa", []),
            "stats": tim.get("statistik_5_laga", {}),
            "matches": tim.get("riwayat_pertandingan", []),
            "strength": _team_strength(tim),
        })

    result = {}
    for g, teams in groups.items():
        teams.sort(key=lambda t: -t["strength"])
        for i, t in enumerate(teams):
            t["group_rank"] = i + 1
            t["points"] = sum(3 for m in t["matches"] if m["status"] == "M") + sum(1 for m in t["matches"] if m["status"] == "S")

        predictions = []
        played = set()
        for t in teams:
            for m in t["matches"]:
                key = tuple(sorted([t["nama"], m["lawan"]]))
                if key in played:
                    continue
                played.add(key)
                opponent = next((ot for ot in teams if ot["nama"] == m["lawan"]), None)
                home_str = t["strength"] if m.get("posisi") == "Home" else (opponent["strength"] if opponent else 50)
                away_str = opponent["strength"] if opponent else 50
                total = home_str + away_str + 0.01
                home_prob = round(home_str / total * 100, 1)
                away_prob = round(away_str / total * 100, 1)
                draw_prob = round(100 - home_prob - away_prob, 1)
                if m["status"] == "M":
                    if m.get("posisi") == "Home":
                        winner, conf = t["nama"], home_prob
                    else:
                        winner, conf = m["lawan"], away_prob
                elif m["status"] == "S":
                    winner, conf = "Draw", draw_prob
                else:
                    winner, conf = m["lawan"], away_prob if m.get("posisi") == "Home" else home_prob
                predictions.append({
                    "home_team": t["nama"] if m.get("posisi") == "Home" else m["lawan"],
                    "away_team": m["lawan"] if m.get("posisi") == "Home" else t["nama"],
                    "score": m["skor"],
                    "date": m["tanggal"],
                    "status": m["status"],
                    "predicted_winner": winner,
                    "confidence": conf,
                    "home_prob": home_prob,
                    "draw_prob": draw_prob,
                    "away_prob": away_prob,
                })

        result[g] = {
            "standings": [{"rank": t["group_rank"], "nama": t["nama"], "logo": t["logo"],
                           "points": t["points"], "strength": t["strength"],
                           "form": t["form"], "stats": t["stats"],
                           "played": len(t["matches"]),
                           "won": sum(1 for m in t["matches"] if m["status"] == "M"),
                           "drawn": sum(1 for m in t["matches"] if m["status"] == "S"),
                           "lost": sum(1 for m in t["matches"] if m["status"] == "K"),
                           "goals_for": t["stats"].get("gol_dicetak", 0),
                           "goals_against": t["stats"].get("gol_kemalingan", 0),
                           "clean_sheets": t["stats"].get("clean_sheets", 0)} for t in teams],
            "predictions": predictions,
        }

    return result
