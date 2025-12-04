# Farm Planner

A web app for optimizing fertilizer and water usage in farming. Helps you figure out the right NPK ratios and irrigation schedules without wasting money or resources.

## What it does

**Fertilizer Planner**
- Calculate optimal N-P-K ratios for your field
- Get recommendations for actual products (DAP, Urea, MOP, etc.)
- Balance between yield, cost, and environmental impact
- Visual charts to compare different options

**Water Planner**
- Weekly irrigation schedules for Rice, Wheat, Maize, and Cotton
- Supports different irrigation methods (flood, sprinkler, drip)
- Adjusts for rainfall and crop growth stages
- Shows total water needed for the season

## Setup

You'll need Node.js and Python installed.

```bash
# Install Python stuff
pip install -r requirements.txt

# Install Node stuff
cd my-react-app
npm install

# Run everything
npm run dev
```

The app will open at `http://localhost:5173`. The dev command runs both the React frontend and Streamlit backend together.

## Stack

- React + Vite for the frontend
- Streamlit for the backend UI
- NumPy/Pandas for calculations
- Plotly for charts

## How it works

The fertilizer planner runs a grid search over different NPK combinations and uses Pareto optimization to find the best trade-offs. Basically it tries a bunch of combinations and shows you which ones aren't strictly worse than others.

Water planning uses standard crop coefficient curves (Kc values) that change through the growing season, adjusted for your irrigation method's efficiency.

## Project structure

```
├── my-react-app/       # React frontend (just wraps Streamlit in an iframe)
├── app.py              # Main Streamlit app with all the logic
└── requirements.txt    # Python dependencies
```

## Notes

- Start with reasonable limits (like 200-150-150 for NPK) and adjust from there
- The "goal" selector changes how it weighs yield vs cost vs environmental impact
- Download buttons save your plans as text files

Built this to help with farm planning decisions. Feel free to use or modify however you want.
