"""Step 1 - Download the Hotel Booking Demand dataset (119,390 bookings, two Portuguese hotels)."""
import urllib.request

from config import DATA_URL, RAW_PATH


def main():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists():
        print(f"[get_data] already have {RAW_PATH.name}")
        return
    print(f"[get_data] downloading {DATA_URL}")
    urllib.request.urlretrieve(DATA_URL, RAW_PATH)


if __name__ == "__main__":
    main()
