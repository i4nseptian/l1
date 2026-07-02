# Football Match Prediction Web App — Design Spec

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Frontend | React (Vite) + Tailwind CSS |
| Backend | Python FastAPI |
| Scraping | Selenium / undetected-chromedriver (sudah ada) |
| Data Tim | Football-Data.org API (gratis) |
| Database | SQLite ringan (riwayat prediksi, cache data tim) |
| Prediction | Rule Engine + Custom Logic + ML (future) |

---

## Architecture

```
React (Vite) ──HTTP──> FastAPI ──> Football-Data.org API
                            ├──> SQLite DB (cache + history)
                            ├──> 1xBet Scraper (real-time odds)
                            └──> Prediction Engine
                                  ├── Rule-based scorer
                                  ├── Custom logic (user input)
                                  └── ML model (future)
```

---

## Data Flow

1. **User** buka halaman Dashboard
2. **FastAPI** scrape data pertandingan live dari 1xBet
3. **FastAPI** ambil data tim (form, klasemen) dari Football-Data.org
4. **FastAPI** load faktor bet dari file Excel (data faktor statis)
5. **Prediction Engine** proses semua data → hasil prediksi
6. **React** render kartu pertandingan dengan indikator

---

## Halaman & Fitur Detail

### 1. Dashboard `/`

**Layout:**
- Navbar atas: logo + navigation
- Filter bar: pilih **Liga/Negara** (dropdown), **Tanggal**
- Grid kartu pertandingan (3 kolom desktop, 1 kolom mobile)

**Setiap kartu menampilkan:**
- Tim Home vs Tim Away (nama + logo jika ada)
- Odds 1X2 (angka besar dari 1xBet)
- **Indikator Prediksi** — badge warna:
  - 🟢 Hijau ≥80% — "Home Win"
  - 🟡 Kuning 60-79% — "Lean Home"
  - 🔴 Merah <60% — "No Clear Pick"
- Waktu pertandingan (Live / 90'+ / jam)
- Klik kartu → masuk halaman detail

### 2. Detail Pertandingan `/match/:id`

**Header:**
- Tim Home (logo, nama) vs Tim Away (logo, nama)
- Skor (jika live) / VS (belum mulai)
- Waktu / menit pertandingan

**Tab 1: Info Tim**
- Form 5 laga terakhir (✅ / ❌ / ➖)
- Klasemen (posisi, P, W, D, L, Pts)
- Head-to-Head 5 pertemuan terakhir

**Tab 2: Faktor Bet**
- Load dari data Excel 1xBet — semua jenis pasar yang tersedia:
  - 1X2, Double Chance, Both Teams to Score
  - Over/Under (0.5, 1.5, 2.5, 3.5, 4.5, 5.5)
  - Handicap Asia
  - Total Goals, Exact Goals
  - Tendangan Sudut, Kartu, Offside, Pelanggaran
  - Gol di kedua babak
  - Semua TG (tournament group) dari data: ["Tendangan Sudut", "Kartu", "Pelanggaran", "Gol yang diharapkan", "Tembakan Pada Gawang", "Duel udara", "Tackle", "Intersepsi", dll — lihat data explore]
- Setiap pasar: odds terkini, pergerakan (naik/turun)
- Grafik batang perbandingan odds antar bookmaker (jika ada)

**Tab 3: Prediksi**
- **Confidence Score** — angka 0-100% dengan breakdown:
  - Form Home (25%) — skor dari 5 laga terakhir
  - Form Away (25%) — skor dari 5 laga terakhir
  - Head-to-Head (15%) — hasil pertemuan sebelumnya
  - Klasemen (10%) — posisi liga, poin
  - Odds Movement (15%) — pergerakan odds indikasi pasar
  - Faktor Bet (10%) — jenis pasar yang tersedia & kecenderungan
- **Rekomendasi:** "Recommended Bet: Home Win 1.85"
- **Penjelasan singkat:** kalimat seperti "Home unggul form 4/5 vs Away 1/5, odds turun dari 2.0 ke 1.85"

**Tab 4: Logika Saya**
- Form isi aturan kustom berbentuk **IF-THEN** sederhana:
  - Dropdown: pilih kondisi (Odds Home < 2.0, Form Home >= 3 menang, H2H Home dominan, dll)
  - Operator: AND / OR
  - Hasil: Rekomendasi (Home / Draw / Away) + bobot prioritas
- Tombol "Simpan Logika" — disimpan di database untuk dipakai tiap prediksi
- Bisa tambah banyak aturan, disusun prioritas

### 3. Halaman Riwayat `/history`

- Tabel prediksi yang sudah dibuat
- Kolom: Tanggal, Tim, Prediksi, Hasil Aktual, Akurat? (✅/❌)
- Statistik akurasi (minggu ini, bulan ini, overall)
- Grafik akurasi per jenis pasar

### 4. Halaman Data Faktor `/factors`

- Menampilkan semua faktor bet dari file Excel dalam bentuk tabel
- Filter berdasarkan TG (Tendangan Sudut, Kartu, dll)
- Bisa eksplor jenis pasar apa saja yang tersedia di 1xBet

---

## Backend API Endpoints

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/leagues` | Daftar liga tersedia |
| GET | `/api/matches?league=X&date=Y` | Pertandingan dengan prediksi |
| GET | `/api/matches/:id` | Detail pertandingan |
| GET | `/api/matches/:id/odds` | Odds & faktor bet detail |
| GET | `/api/matches/:id/prediction` | Hasil prediksi + breakdown |
| POST | `/api/custom-logic` | Simpan aturan logika user |
| GET | `/api/custom-logic` | Ambil aturan logika user |
| GET | `/api/history` | Riwayat prediksi |
| GET | `/api/factors` | Semua faktor bet dari Excel |
| GET | `/api/team/:id` | Data tim (form, klasemen, pemain) |

---

## Prediction Engine

### Scoring Formula (Sementara)

```
Score Home = (W1 × FormHome) + (W2 × H2HHome) + (W3 × ClassHome) + (W4 × OddsMovHome) + (W5 × FactorBet)
Score Away = (W1 × FormAway) + (W2 × H2HAway) + (W3 × ClassAway) + (W4 × OddsMovAway) + (W5 × FactorBet)
Draw Score = (W2 × H2HDraw) + ...

Confidence = max(Score Home, Draw, Score Away) / Total × 100%
```

Bobot W1-W5 bisa disesuaikan, default: [0.25, 0.15, 0.10, 0.15, 0.10]

### Custom Logic

User bisa menambahkan aturan yang **override** atau **menambah bobot**:
```
IF OddsHome < 1.50 AND FormHome > 3 AND AwayTopScorerInjured = true
THEN +20% Home Score
```

### ML Model (Future)

- Kumpulkan data historis (prediksi vs hasil aktual)
- Training model sederhana (RandomForest / XGBoost)
- Model sebagai pelengkap, rule-based tetap jalan

---

## Database Schema (SQLite)

```sql
-- Pertandingan & odds
CREATE TABLE matches (
  id INTEGER PRIMARY KEY,
  league TEXT,
  home_team TEXT,
  away_team TEXT,
  home_score INTEGER,
  away_score INTEGER,
  status TEXT,          -- live / finished / scheduled
  match_time DATETIME,
  odds_home REAL,
  odds_draw REAL,
  odds_away REAL,
  created_at DATETIME
);

-- Prediksi
CREATE TABLE predictions (
  id INTEGER PRIMARY KEY,
  match_id INTEGER,
  predicted_winner TEXT,  -- home / draw / away
  confidence REAL,
  is_correct BOOLEAN,
  actual_result TEXT,
  created_at DATETIME,
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Logika kustom user
CREATE TABLE custom_logic (
  id INTEGER PRIMARY KEY,
  condition_field TEXT,      -- odds_home, form_home, dll
  operator TEXT,             -- <, >, =, >=, <=
  condition_value REAL,
  logic_connector TEXT,      -- AND / OR
  result_recommendation TEXT, -- home / draw / away
  weight_modifier REAL,      -- +20, -10, dll
  priority INTEGER,
  is_active BOOLEAN DEFAULT 1,
  created_at DATETIME
);

-- Faktor bet dari Excel
CREATE TABLE bet_factors (
  id INTEGER PRIMARY KEY,
  group_name TEXT,           -- TG: "Tendangan Sudut", "Kartu", dll
  market_type TEXT,          -- MT: 2=Popular, 3=Total, dll
  market_name TEXT,          -- N: "Populer", "Total", dll
  event_count INTEGER,       -- EC
  created_at DATETIME
);

-- Data tim (cache dari Football-Data.org)
CREATE TABLE teams (
  id INTEGER PRIMARY KEY,
  name TEXT,
  league TEXT,
  form TEXT,                  -- "WWDLW"
  position INTEGER,
  points INTEGER,
  played INTEGER,
  won INTEGER,
  drawn INTEGER,
  lost INTEGER,
  last_updated DATETIME
);
```

---

## Project Structure

```
D:\scraping\
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # SQLite setup
│   ├── scraper/
│   │   ├── _1xbet.py         # Scraper 1xBet (dari file yang sudah ada)
│   │   └── football_data.py  # Football-Data.org client
│   ├── prediction/
│   │   ├── engine.py         # Rule-based scorer
│   │   ├── custom_logic.py   # User custom logic processor
│   │   └── ml_model.py       # ML model (future)
│   └── data/
│       └── factors.json      # Parsed data dari Excel
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MatchDetail.jsx
│   │   │   ├── History.jsx
│   │   │   └── Factors.jsx
│   │   ├── components/
│   │   │   ├── MatchCard.jsx
│   │   │   ├── PredictionBadge.jsx
│   │   │   ├── FormChart.jsx
│   │   │   ├── OddsTable.jsx
│   │   │   └── CustomLogicForm.jsx
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── docs/superpowers/specs/
│   └── 2026-07-01-football-prediction-app-design.md
├── data scraping ian.xlsx    # Data faktor 1xBet
└── scraper_*.py              # Scraper existing
```

---

## Catatan Data Faktor 1xBet

Dari file Excel, struktur faktor bet:
- `I` — ID unik faktor
- `N` — ID Sport/Tournament (214429 = Football utama)
- `CI` — Championship ID
- `T` — type (1000 = standar)
- `EC` — Event Count (jumlah event tersedia)
- `TG` — Tournament Group: "Tendangan Sudut", "Kartu", "Pelanggaran", "Tendangan Gawang", "Offside", "Duel udara", "Tackle", "Intersepsi", "Lemparan ke dalam", "Tembakan Pada Gawang", "Shot Pada Target", "Gol yang diharapkan", "Penyelamatan", "Dribbling", "Operan", "Pengecekan VAR", "Hasil Alternatif", "Kejadian Cepat", "Tim medis", dll
- `P` — Period (1 = Babak pertama, 2 = Babak ke-2)
- `PN` — Period Name
- `SS` — Status (2 = aktif)
- `MEC` — Array of Market Counts: [{ MT: 2, EC: 121, N: "Populer" }, { MT: 3, EC: 48, N: "Total" }, ...]

---

## Next Steps

1. ✅ **Design doc** (ini)
2. Set up React + FastAPI project
3. Parse data Excel ke JSON terstruktur
4. Build prediction engine dasar
5. Build API endpoints
6. Build frontend pages
7. Integrasi Football-Data.org
8. Fitur custom logic user
9. Testing & deployment
