from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

app = Flask(__name__)
CORS(app)

CSV_FILE = "submissions.csv"
FIELDNAMES = [
    "name",
    "latitude",
    "longitude",
    "notes",
    "priority",
    "due_date",
    "materials",
    "estimated_price",
    "status",
]
MOUSER_SEARCH_URL = "https://api.mouser.com/api/v1/search/keyword"
PART_NUMBER_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z0-9][A-Za-z0-9._/-]*$")


def read_submissions(include_row_id=False):
    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = []

        for row_id, row in enumerate(reader):
            normalized = {
                "name": row.get("name", ""),
                "latitude": row.get("latitude", ""),
                "longitude": row.get("longitude", ""),
                "notes": row.get("notes", ""),
                "priority": row.get("priority") or "medium",
                "due_date": row.get("due_date", ""),
                "materials": row.get("materials", ""),
                "estimated_price": row.get("estimated_price", ""),
                "status": row.get("status") or "incomplete",
            }

            if include_row_id:
                normalized["row_id"] = row_id

            rows.append(normalized)

        return rows


def write_submissions(rows):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in FIELDNAMES} for row in rows)


def parse_materials(materials_text):
    materials = []

    for line in materials_text.splitlines():
        line = line.strip()

        if not line:
            continue

        values = next(csv.reader([line]))
        values = [value.strip() for value in values if value.strip()]

        if not values:
            continue

        quantity = 1
        part_number = ""
        description = ""

        if is_number(values[0]):
            quantity = float(values[0])
            description = ", ".join(values[1:]).strip()
        elif len(values) > 1 and is_number(values[1]):
            part_number = values[0]
            quantity = float(values[1])
            description = ", ".join(values[2:]).strip()
        else:
            description = ", ".join(values).strip()

            if len(values) == 1 and looks_like_part_number(values[0]):
                part_number = values[0]

        search_query = " ".join(value for value in [part_number, description] if value).strip()

        if not search_query:
            search_query = line

        materials.append({
            "part_number": part_number,
            "quantity": quantity,
            "description": description,
            "search_query": search_query,
        })

    return materials


def is_number(value):
    try:
        float(value)
    except ValueError:
        return False

    return True


def looks_like_part_number(value):
    if " " in value:
        return False

    return bool(PART_NUMBER_PATTERN.match(value))


def format_quantity(quantity):
    if float(quantity).is_integer():
        return str(int(quantity))

    return str(quantity)


def query_mouser_parts(search_query):
    api_key = os.environ.get("MOUSER_API_KEY")

    if not api_key:
        raise RuntimeError("Set MOUSER_API_KEY to enable Mouser pricing.")

    payload = json.dumps({
        "SearchByKeywordRequest": {
            "keyword": search_query,
            "records": 10,
            "startingRecord": 0,
            "searchOptions": "None",
            "searchWithYourSignUpLanguage": "false",
        }
    }).encode("utf-8")
    url = f"{MOUSER_SEARCH_URL}?apiKey={urllib.parse.quote(api_key)}"
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        mouser_response = json.loads(response.read().decode("utf-8"))

    errors = mouser_response.get("Errors") or []

    if errors:
        first_error = errors[0]
        message = first_error.get("Message") if isinstance(first_error, dict) else str(first_error)
        raise RuntimeError(message or "Mouser pricing query failed.")

    parts = mouser_response.get("SearchResults", {}).get("Parts", [])

    if not parts:
        raise RuntimeError(f"No Mouser result found for {search_query}.")

    return parts


def parse_price_amount(value):
    if value is None:
        raise ValueError("Missing price amount.")

    cleaned = str(value).replace("$", "").replace(",", "").strip()
    return float(cleaned)


def choose_price_tier(price_tiers, quantity):
    if not price_tiers:
        return None

    sorted_tiers = sorted(price_tiers, key=lambda tier: int(tier.get("Quantity", 0) or 0))
    chosen_tier = sorted_tiers[0]

    for tier in sorted_tiers:
        if quantity >= int(tier.get("Quantity", 0) or 0):
            chosen_tier = tier

    return chosen_tier


def find_best_mouser_part(parts, quantity):
    best_match = None

    for part in parts:
        price_tier = choose_price_tier(part.get("PriceBreaks", []), quantity)

        if not price_tier:
            continue

        unit_price = parse_price_amount(price_tier.get("Price"))

        if best_match is None or unit_price < best_match["unit_price"]:
            best_match = {
                "part": part,
                "unit_price": unit_price,
                "price_break_quantity": price_tier.get("Quantity", ""),
                "currency": price_tier.get("Currency", "USD"),
            }

    return best_match


def estimate_materials_price(materials_text):
    materials = parse_materials(materials_text)

    if not materials:
        return {
            "success": True,
            "total": "",
            "items": [],
            "message": "No materials entered.",
        }

    total = 0
    items = []

    try:
        for material in materials:
            parts = query_mouser_parts(material["search_query"])
            best_match = find_best_mouser_part(parts, material["quantity"])

            if not best_match:
                raise RuntimeError(f"No Mouser price returned for {material['search_query']}.")

            part = best_match["part"]
            unit_price = best_match["unit_price"]
            line_total = unit_price * material["quantity"]
            total += line_total
            items.append({
                **material,
                "matched_part_number": part.get("ManufacturerPartNumber", ""),
                "mouser_part_number": part.get("MouserPartNumber", ""),
                "manufacturer": part.get("Manufacturer", ""),
                "seller": "Mouser",
                "unit_price": round(unit_price, 2),
                "line_total": round(line_total, 2),
                "price_break_quantity": best_match["price_break_quantity"],
                "currency": best_match["currency"],
                "availability": part.get("Availability", ""),
                "product_detail_url": part.get("ProductDetailUrl", ""),
            })
    except (RuntimeError, urllib.error.URLError, KeyError, ValueError) as error:
        return {
            "success": False,
            "total": "",
            "items": items,
            "message": str(error),
        }

    return {
        "success": True,
        "total": round(total, 2),
        "items": items,
        "message": "Estimated with Mouser pricing.",
    }

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    name = data.get("name", "")
    lat = data.get("latitude", "")
    lon = data.get("longitude", "")
    desc = data.get("notes", "")
    priority = data.get("priority", "medium")
    due_date = data.get("due_date", "")
    materials = data.get("materials", "")
    estimate = estimate_materials_price(materials)

    rows = read_submissions()
    rows.append({
        "name": name,
        "latitude": lat,
        "longitude": lon,
        "notes": desc,
        "priority": priority,
        "due_date": due_date,
        "materials": materials,
        "estimated_price": estimate["total"] if estimate["success"] else "",
        "status": "incomplete",
    })
    write_submissions(rows)

    return jsonify({"success": True, "message": "Saved to CSV"})


@app.route("/submissions", methods=["GET"])
def submissions():
    return jsonify(read_submissions(include_row_id=True))


@app.route("/estimate-price", methods=["POST"])
def estimate_price():
    data = request.json or {}
    estimate = estimate_materials_price(data.get("materials", ""))
    return jsonify(estimate)


@app.route("/complete", methods=["POST"])
def complete():
    data = request.json
    row_id = data.get("row_id")

    try:
        row_index = int(row_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid row id"}), 400

    rows = read_submissions()

    if row_index < 0 or row_index >= len(rows):
        return jsonify({"success": False, "message": "Project not found"}), 404

    rows.pop(row_index)
    write_submissions(rows)

    return jsonify({"success": True, "message": "Project completed"})

if __name__ == "__main__":
    app.run(debug=True)
