"""Paths and the business assumptions behind the overbooking simulation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "hotel_bookings.csv"
DB_PATH = ROOT / "data" / "hotel.duckdb"
SQL_DIR = ROOT / "sql"
FIG_DIR = ROOT / "reports" / "figures"
TABLE_DIR = ROOT / "reports" / "tables"

DATA_URL = ("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/"
            "data/2020/2020-02-11/hotels.csv")

# ---- Overbooking simulation (City Hotel) -------------------------------------------
HOTEL = "City Hotel"
CAPACITY = 100            # results are reported per 100 rooms, so they scale to any size

# Cost of "walking" a guest (no room for them on arrival), as a multiple of ADR:
# pay for a comparable room nearby at short-notice rates (~1.3x), transport and a goodwill
# credit (~0.5x), and the risk the guest never books again (~0.7x).
WALK_COST_MULTIPLIER = 2.5

OVERBOOK_LEVELS = [i / 100 for i in range(0, 31)]   # 0% .. 30% above capacity
N_SIMULATIONS = 20_000
RANDOM_STATE = 7
