# Project Map Tracker

A small local web app for tracking project entries on a Mapbox map. Each project can include coordinates, notes, priority, due date, materials, and an estimated materials price from Mouser.

## Project Files

- `app.py` - Flask API for saving, loading, completing, and pricing project entries
- `index.html` - Browser UI
- `styles.css` - App styling
- `submissions.csv` - Local project data

## API Keys

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

Materials can be entered one per line. 

Examples:

```text
4, SN74S74N flip flop
10, 10k resistor 1/4W
SN74S74N, 4, flip flop
```

When you click **Estimate price**, the Flask API searches Mouser and uses the best available price break for each material. Entries are stored in submissions.csv via the Flask backend

