import os
import json
import requests

PRODUCT_URL = "https://www.nintendo.com/en-ca/store/products/nintendo-switch-2-pro-controller-display-stand-the-legend-of-zelda-40th-anniversary-edition-127076/"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
STATE_FILE = "state.json"

IN_STOCK_PHRASES = ["add to cart", "buy now"]
OUT_OF_STOCK_PHRASES = ["find retailers", "sold out", "coming soon", "notify me", "out of stock"]

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f).get("in_stock", False)
    return False

def save_state(in_stock: bool):
    with open(STATE_FILE, "w") as f:
        json.dump({"in_stock": in_stock}, f)

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(PRODUCT_URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False
    text = resp.text.lower()
    has_in_stock = any(p in text for p in IN_STOCK_PHRASES)
    has_blocker = any(p in text for p in OUT_OF_STOCK_PHRASES)
    return has_in_stock and not has_blocker

def notify():
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data="The Zelda 40th Anniversary Pro Controller + stand looks IN STOCK!".encode("utf-8"),
        headers={"Title": "Zelda controller may be in stock!", "Priority": "urgent", "Click": PRODUCT_URL},
    )

def main():
    was_in_stock = load_last_state()
    is_in_stock = check_stock()
    if is_in_stock and not was_in_stock:
        notify()
        print("Stock detected — notification sent.")
    else:
        print(f"No change. in_stock={is_in_stock}")
    save_state(is_in_stock)

if __name__ == "__main__":
    main()
