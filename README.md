# Project Map Tracker

A small local web app for tracking project entries on a Mapbox map. Each project can include coordinates, notes, priority, due date, materials, and an estimated materials price from Mouser.

## Features

- Add project entries through a browser form
- Store entries in `submissions.csv`
- Display projects in a stacked table layout
- Show project markers on a Mapbox map
- Mark projects complete and remove them from the CSV
- Track priority with a colored cellular-style signal icon
- Estimate material costs through the Mouser Search API

## Project Files

- `app.py` - Flask API for saving, loading, completing, and pricing project entries
- `index.html` - Browser UI
- `styles.css` - App styling
- `submissions.csv` - Local project data

## Requirements

- Python 3
- Flask
- Flask-CORS
- A Mapbox public token for the map
- A Mouser Search API key for material pricing

Install Python dependencies:

```bash
pip3 install flask flask-cors
```

## API Keys

The app does not store API keys in the repo.

Set your Mouser API key in the terminal before starting Flask:

```bash
export MOUSER_API_KEY="your-mouser-api-key"
```

The Mapbox token is entered in the browser. Use a public Mapbox token that starts with `pk.`.

## Run The App

Start the Flask API:

```bash
python3 app.py
```

In another terminal, serve the frontend:

```bash
python3 -m http.server 8001
```

Open:

```text
http://127.0.0.1:8001/index.html
```

Paste your Mapbox public token and click **Load map**. After the map loads, the token field is hidden.

## Material Input Format

Materials can be entered one per line. The app supports:

```text
quantity, description
description
part number, quantity, description
```

Examples:

```text
4, SN74S74N flip flop
10, 10k resistor 1/4W
SN74S74N, 4, flip flop
```

When you click **Estimate price**, the Flask API searches Mouser and uses the best available price break for each material.

## CSV Columns

`submissions.csv` uses:

```text
name,latitude,longitude,notes,priority,due_date,materials,estimated_price,status
```

## Notes

- Restart `app.py` after changing environment variables.
- Mouser pricing works best for electronic and electromechanical components.
- General construction materials, lumber, paint, and generic hardware may not price well through Mouser.
- Keep API keys out of committed files.
