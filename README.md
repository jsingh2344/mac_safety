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
4, brick
3, wire
10, rod
```

When you click **Estimate price**, the Flask API searches Mouser and uses the best available price break for each material. Entries are stored in submissions.csv via the Flask backend

#Usage pics:

Example one:
<p>
  <img width="3024" height="1726" alt="image" src="https://github.com/user-attachments/assets/5add2179-626a-4097-b3b5-4f56d66c5cff" />
</p>
Here, I am entering a new project titled 'Project 1', and at coordinates 40, -95. My description is 'Missouri project' and the materials required are 4 bricks, 3 wires, and 10 rods, which has an estimated $340 cost according to the Mouser API. The project due date is Jan. 1, 2027. 

<p>
  <img width="3024" height="1724" alt="image" src="https://github.com/user-attachments/assets/360d5554-f7f0-44ef-afe1-a45c0cbb2828" />
</p>
Now I've entered the project. The project location pin is visible north of Saint Joseph, MO, and the entry has been added to the table in the left side of the page. All of the entered project attributes are visible, along with an 'incomplete' status and a 'complete' button. Clicking the button will remove the entry
<p>
  <img width="3024" height="1724" alt="image" src="https://github.com/user-attachments/assets/a99f99c2-0df1-49f4-8417-782ee5d44f41" />
</p>
Adding a second entry, this time with different materials and a 'High' priority level.
<p>
  <img width="3024" height="1732" alt="image" src="https://github.com/user-attachments/assets/9d23675b-fbe1-4ac7-b12d-ff286f16f591" />
</p>
The map and table after adding the second project.


