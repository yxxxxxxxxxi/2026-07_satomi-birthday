from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "trip.yaml"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "output"

SIGHTSEEING_PATH = DATA_DIR / "sightseeing_candidates.csv"
HOTEL_PATH = DATA_DIR / "hotel_candidates.csv"
RESTAURANT_PATH = DATA_DIR / "restaurant_candidates.csv"
TRANSPORT_PATH = DATA_DIR / "transport_options.csv"

MYMAPS_OUTPUT_PATH = OUTPUT_DIR / "mymaps_import.csv"
DASHBOARD_OUTPUT_PATH = OUTPUT_DIR / "travel_dashboard.html"
PAGES_INDEX_OUTPUT_PATH = OUTPUT_DIR / "index.html"

DOC_TAB_FILES = [
    ("overview", "概要", DOCS_DIR / "00_overview.md"),
    ("itinerary", "旅程表", DOCS_DIR / "01_itinerary.md"),
    ("sightseeing_doc", "観光候補", DOCS_DIR / "02_sightseeing.md"),
    ("hotels_doc", "宿泊候補", DOCS_DIR / "03_hotels.md"),
    ("restaurants_doc", "食事候補", DOCS_DIR / "04_restaurants.md"),
    ("transport_doc", "移動", DOCS_DIR / "05_transport.md"),
    ("budget_doc", "予算", DOCS_DIR / "06_budget.md"),
    ("reservations_doc", "予約・ToDo", DOCS_DIR / "07_reservations_todo.md"),
    ("birthday_doc", "誕生日演出", DOCS_DIR / "08_birthday_surprise.md"),
    ("notes_doc", "メモ", DOCS_DIR / "09_notes.md"),
]

DAY_ORDER = ["Day1", "Day2", "Day3", "Day4", "未定"]
ALLOWED_PRIORITIES = {"S", "A", "B", "C"}
ALLOWED_HEAT_RISK = {"高", "中", "低"}
ALLOWED_RAIN_OK = {"可", "一部可", "不可"}
ALLOWED_DAY_CANDIDATES = set(DAY_ORDER)
REQUIRED_SIGHTSEEING_COLUMNS = [
    "id",
    "name",
    "area",
    "category",
    "priority",
    "address",
    "latitude",
    "longitude",
    "day_candidate",
    "stay_minutes",
    "birthday_score",
    "heat_risk",
    "rain_ok",
    "memo",
    "source_url",
    "google_maps_search",
]
