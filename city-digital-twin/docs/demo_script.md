# Demo Script (7-Minute Walkthrough)

## Setup (Before Demo)
1. Run `pip install -r requirements.txt`
2. Run `python scripts/generate_sample_data.py`
3. Run `python backend/main.py`
4. Open `http://localhost:8000`

---

## Minute 1: Introduction
**Say:** "This is City Digital Twin — a disaster simulation platform that helps city planners visualize how floods and earthquakes affect urban infrastructure."

**Show:** The dark map interface centered on India.

---

## Minute 2: Load a City
**Do:** Select **Mumbai** from the city dropdown.

**Show:** The map flies to Mumbai. Facility markers (hospitals, fire stations, shelters) appear.

**Say:** "The system loads building footprints, road networks, and emergency facilities. Data comes from OpenStreetMap with synthetic enrichment."

---

## Minute 3: Flood Simulation
**Do:**
1. Ensure **FLOOD** tab is active
2. Set Rainfall to **200mm**
3. Set Duration to **6 hours**
4. Set Curve Number to **85**
5. Click **Simulate Flood**

**Show:** Loading overlay with status messages. Flood zones appear in blue. Buildings change color by damage state. Blocked roads turn red.

**Say:** "The system uses the SCS Curve Number method to calculate surface runoff, then routes water downhill using the elevation model. Each building is assessed for flood damage."

---

## Minute 4: Review Results
**Show:** The statistics cards showing:
- Affected area in km²
- Buildings at risk
- Roads blocked percentage
- Hospitals isolated

**Show:** The damage doughnut chart.

**Do:** Click on a building to show the risk popup.

**Say:** "Each building gets an AI risk score from 0 to 100, combining hazard exposure, structural vulnerability, and building importance. You can see the contributing risk factors."

---

## Minute 5: Resource Optimization
**Do:** Click **Optimize Emergency Resources**.

**Show:** Green resource markers appear with coverage radius circles.

**Say:** "The system uses a greedy set-cover algorithm to find optimal positions for rescue boats, maximizing coverage of at-risk buildings."

---

## Minute 6: Earthquake Simulation
**Do:**
1. Switch to **EARTHQUAKE** tab
2. Set Magnitude to **7.5**
3. Set Depth to **10km**
4. Click on the map to set the epicenter
5. Click **Simulate Earthquake**

**Show:** Buildings in 3D colored by damage state. The seismic wave animation at the epicenter.

**Say:** "The earthquake model calculates Peak Ground Acceleration using seismic attenuation formulas and applies HAZUS fragility curves for each structural type."

---

## Minute 7: Layer Controls and Wrap-up
**Do:**
1. Toggle the **Risk Heatmap** layer on
2. Toggle other layers on/off to show flexibility

**Say:** "The platform works entirely offline with synthetic data, handles any city with OpenStreetMap coverage, and runs simulations in under 10 seconds. It's built for real-world emergency planning and hackathon demonstrations."

---

## Key Talking Points
- Uses real physics models (SCS Curve Number, seismic attenuation)
- AI damage prediction with XGBoost (auto-trains on first run)
- Infrastructure graph analysis identifies critical road segments
- Works completely offline with synthetic data
- Sub-10-second simulation performance
