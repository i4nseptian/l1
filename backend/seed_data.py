"""Seed database with base leagues from around the world."""
from database import init_db, get_db

LEAGUES = [
    # EUROPE
    ('English Premier League', 'England'),
    ('EFL Championship', 'England'),
    ('EFL League One', 'England'),
    ('EFL League Two', 'England'),
    ('La Liga', 'Spain'),
    ('La Liga 2', 'Spain'),
    ('Serie A', 'Italy'),
    ('Serie B', 'Italy'),
    ('Bundesliga', 'Germany'),
    ('Bundesliga 2', 'Germany'),
    ('3. Liga', 'Germany'),
    ('Ligue 1', 'France'),
    ('Ligue 2', 'France'),
    ('Eredivisie', 'Netherlands'),
    ('Eerste Divisie', 'Netherlands'),
    ('Primeira Liga', 'Portugal'),
    ('Liga Portugal 2', 'Portugal'),
    ('Scottish Premiership', 'Scotland'),
    ('Belgian Pro League', 'Belgium'),
    ('Swiss Super League', 'Switzerland'),
    ('Austrian Bundesliga', 'Austria'),
    ('Danish Superliga', 'Denmark'),
    ('Swedish Allsvenskan', 'Sweden'),
    ('Norwegian Eliteserien', 'Norway'),
    ('Polish Ekstraklasa', 'Poland'),
    ('Czech First League', 'Czech Republic'),
    ('Greek Super League', 'Greece'),
    ('Turkish Super Lig', 'Turkey'),
    ('Russian Premier League', 'Russia'),
    ('Ukrainian Premier League', 'Ukraine'),
    ('Croatian HNL', 'Croatia'),
    ('Serbian SuperLiga', 'Serbia'),
    ('Romanian Liga I', 'Romania'),
    ('Bulgarian First League', 'Bulgaria'),
    ('Hungarian NB I', 'Hungary'),
    ('Slovak Super Liga', 'Slovakia'),
    ('Slovenian PrvaLiga', 'Slovenia'),
    ('Cypriot First Division', 'Cyprus'),
    ('Israeli Premier League', 'Israel'),

    # AMERICAS
    ('MLS', 'United States'),
    ('Liga MX', 'Mexico'),
    ('Campeonato Brasileiro Série A', 'Brazil'),
    ('Campeonato Brasileiro Série B', 'Brazil'),
    ('Argentine Primera División', 'Argentina'),
    ('Chilean Primera División', 'Chile'),
    ('Colombian Primera A', 'Colombia'),
    ('Peruvian Liga 1', 'Peru'),
    ('Uruguayan Primera División', 'Uruguay'),
    ('Paraguayan Primera División', 'Paraguay'),
    ('Ecuadorian Serie A', 'Ecuador'),
    ('Bolivian Primera División', 'Bolivia'),
    ('Venezuelan Primera División', 'Venezuela'),

    # ASIA
    ('J1 League', 'Japan'),
    ('J2 League', 'Japan'),
    ('K League 1', 'South Korea'),
    ('Chinese Super League', 'China'),
    ('Saudi Pro League', 'Saudi Arabia'),
    ('UAE Pro League', 'United Arab Emirates'),
    ('Qatar Stars League', 'Qatar'),
    ('Iran Pro League', 'Iran'),
    ('Thai League 1', 'Thailand'),
    ('A-League', 'Australia'),
    ('Indian Super League', 'India'),
    ('Malaysia Super League', 'Malaysia'),
    ('Indonesian Liga 1', 'Indonesia'),
    ('Vietnamese V.League 1', 'Vietnam'),

    # AFRICA
    ('Egyptian Premier League', 'Egypt'),
    ('Moroccan Botola Pro', 'Morocco'),
    ('Tunisian Ligue 1', 'Tunisia'),
    ('Algerian Ligue 1', 'Algeria'),
    ('South African Premier Division', 'South Africa'),
    ('Nigerian Professional League', 'Nigeria'),
    ('Ghana Premier League', 'Ghana'),

    # INTERNATIONAL
    ('World Cup', 'International'),
    ('European Championship', 'International'),
    ('Copa America', 'International'),
    ('Africa Cup of Nations', 'International'),
    ('Asian Cup', 'International'),
    ('CONCACAF Gold Cup', 'International'),
    ('UEFA Champions League', 'International'),
    ('UEFA Europa League', 'International'),
    ('UEFA Conference League', 'International'),
    ('Copa Libertadores', 'International'),
    ('Copa Sudamericana', 'International'),
    ('AFC Champions League', 'International'),
    ('CAF Champions League', 'International'),
    ('FIFA Club World Cup', 'International'),
]


def seed():
    init_db()
    conn = get_db()
    for name, country in LEAGUES:
        conn.execute(
            "INSERT OR IGNORE INTO leagues (name, country) VALUES (?, ?)",
            (name, country)
        )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) as c FROM leagues").fetchone()['c']
    conn.close()
    print(f"Seeded {total} leagues from {len(set(l[1] for l in LEAGUES))} countries")
    print("To sync real teams: POST /api/teams/sync")
    print("To sync from 1xBet: POST /api/teams/sync-from-scraper")


if __name__ == '__main__':
    seed()
