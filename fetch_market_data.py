"""Fetch market results or start the provider-neutral web application."""

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RESULTS_URL = "https://matkaonline.games/front/fetch_updated_results"
MARKETS = {
    "59": "MILAN MORNING",
    "65": "TIME BAZAR MORNING",
    "60": "SRIDEVI",
    "53": "MADHURI DAY",
    "74": "KALYAN MORNING",
    "1": "TIME BAZAR",
    "54": "MADHUR DAY",
    "2": "TARA MUMBAI DAY",
    "70": "MAIN SRIDEVI DAY",
    "37": "RAJDHANI DAY",
    "73": "MILAN DAY",
    "45": "MAIN MUMBAI DAY",
    "63": "SUPREME DAY",
    "43": "KALYAN",
    "16": "SUPER MATKA",
    "67": "MADHURI NIGHT",
    "61": "SRIDEVI NIGHT",
    "72": "MADHUR NIGHT",
    "17": "TARA MUMBAI NIGHT",
    "64": "SUPREME NIGHT",
    "71": "MILAN NIGHT",
    "38": "RAJDHANI NIGHT",
    "42": "KALYAN NIGHT",
    "58": "MAIN BAZAR",
}


def published_value(record, value_key, status_key, placeholder):
    value = record.get(value_key)
    if str(record.get(status_key)) != "1" or value is None:
        return placeholder
    return str(value)


def format_panel(record, digit_key, status_key):
    digit = published_value(record, digit_key, status_key, "***")
    return "000" if digit == "0" else digit


def fetch_raw_market_data():
    request = Request(
        RESULTS_URL,
        headers={
            "User-Agent": "Newgen-Market-Results/1.0",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=20) as response:
        data = json.load(response)

    if not isinstance(data, list):
        raise ValueError("The results endpoint returned an unexpected response.")

    if any(not isinstance(record, dict) or "id" not in record for record in data):
        raise ValueError("The results endpoint returned an invalid market record.")
    return data


def fetch_market_data():
    results = []
    for record in fetch_raw_market_data():
        market_id = str(record["id"])
        open_result = published_value(record, "open_result", "open_stat", "*")
        close_result = published_value(record, "close_result", "close_stat", "*")
        results.append(
            {
                "id": market_id,
                "market": MARKETS.get(market_id, f"Market {market_id}"),
                "open_panel": format_panel(record, "open_digit", "open_stat"),
                "jodi": f"{open_result}{close_result}",
                "close_panel": format_panel(record, "close_digit", "close_stat"),
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch market results or serve the provider-neutral website."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable JSON instead of a table",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="serve the FastAPI application (requires PostgreSQL and Redis)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="server bind address")
    parser.add_argument("--port", type=int, default=8000, help="server port")
    args = parser.parse_args()

    if args.serve:
        import uvicorn

        print(f"Serving website at http://{args.host}:{args.port}/")
        uvicorn.run("app.main:app", host=args.host, port=args.port)
        return

    try:
        results = fetch_market_data()
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as error:
        parser.exit(1, f"Could not fetch market data: {error}\n")

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"{'Market':<24} {'Open':<8} {'Jodi':<6} {'Close':<8}")
    print("-" * 50)
    for result in results:
        print(
            f"{result['market']:<24} {result['open_panel']:<8} "
            f"{result['jodi']:<6} {result['close_panel']:<8}"
        )


if __name__ == "__main__":
    main()
