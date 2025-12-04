import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Farm Planner", page_icon="🌾", layout="wide")

# Data
CROPS = {"Rice": 45, "Wheat": 30, "Maize": 35, "Cotton": 50}
IRRIGATION = {"Flood": 0.60, "Sprinkler": 0.75, "Drip": 0.90}

def calc_yield(n, p, k):
    return np.log1p(0.06*n + 0.05*p + 0.04*k) * 100

def calc_cost(n, p, k, cn, cp, ck):
    return cn*n + cp*p + ck*k

def calc_impact(n, p, k):
    return 0.002*n**2 + 0.003*p**2 + 0.0025*k**2

def find_pareto(df):
    """Keep only non-dominated solutions"""
    vals = df[['Yield', 'Cost', 'Env']].values
    vals[:, 0] = -vals[:, 0]  # Flip yield (higher is better)
    
    dominated = np.zeros(len(vals), dtype=bool)
    for i in range(len(vals)):
        if not dominated[i]:
            better = np.all(vals <= vals[i], axis=1) & np.any(vals < vals[i], axis=1)
            better[i] = False
            dominated |= better
    return df[~dominated].copy()

def get_products(n, p, k):
    """Get fertilizer product recommendations"""
    dap = p / 0.46
    urea = max(0, n - dap*0.18) / 0.46
    mop = k / 0.60
    
    return [
        ("Yield Booster", [("DAP", dap), ("Urea", urea), ("MOP", mop)]),
        ("Cost Saver", [("SSP", p/0.16), ("Urea", n/0.46), ("MOP", mop)]),
        ("Eco-Balanced", [("DAP", dap), ("Urea", urea*0.8), ("MOP", mop), ("Manure", 500)])
    ]

# Main App
planner = st.sidebar.selectbox("Choose Planner", ["Fertilizer", "Water"])

if planner == "Fertilizer":
    st.title("🌾 Fertilizer Planner")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("NPK Limits")
        max_n = st.number_input("Max N", 0, 500, 200)
        max_p = st.number_input("Max P", 0, 500, 150)
        max_k = st.number_input("Max K", 0, 500, 150)
        step = st.number_input("Step", 1, 50, 10)
    
    with col2:
        st.subheader("Costs (₹/unit)")
        cost_n = st.number_input("N Cost", 0, 100, 12)
        cost_p = st.number_input("P Cost", 0, 100, 10)
        cost_k = st.number_input("K Cost", 0, 100, 8)
    
    st.divider()
    col1, col2 = st.columns(2)
    unit = col1.selectbox("Unit", ["acre", "hectare"])
    area = col2.number_input("Area", 0.1, 1000.0, 1.0)
    
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        max_budget = col1.number_input("Max Budget", 0.0)
        max_env = col2.number_input("Max Impact", 0.0)
        min_yield = col3.number_input("Min Yield", 0.0)
        goal = st.selectbox("Goal", ["Balanced", "Save money", "More yield"])
    
    if st.button("Find Plan", type="primary"):
        # Generate all combinations
        n_range = np.arange(0, max_n+1, step)
        p_range = np.arange(0, max_p+1, step)
        k_range = np.arange(0, max_k+1, step)
        n, p, k = [x.ravel() for x in np.meshgrid(n_range, p_range, k_range)]
        
        df = pd.DataFrame({
            'N': n, 'P': p, 'K': k,
            'Yield': calc_yield(n, p, k),
            'Cost': calc_cost(n, p, k, cost_n, cost_p, cost_k),
            'Env': calc_impact(n, p, k)
        })
        
        # Apply filters
        if max_budget > 0: df = df[df.Cost <= max_budget]
        if max_env > 0: df = df[df.Env <= max_env]
        if min_yield > 0: df = df[df.Yield >= min_yield]
        
        if len(df) == 0:
            st.warning("No options match filters")
        else:
            # Find best
            pareto = find_pareto(df)
            norm = lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9)
            weights = {"Save money": [0.5,2,1], "More yield": [2,1,1]}.get(goal, [1,1,1])
            
            normed = pareto[['Yield','Cost','Env']].apply(norm)
            dist = np.linalg.norm((normed.values - [1,0,0]) * weights, axis=1)
            best = pareto.iloc[np.argmin(dist)]
            
            acres = area * (2.47 if unit == "hectare" else 1)
            st.success(f"N={int(best.N)}, P={int(best.P)}, K={int(best.K)} | Cost: ₹{best.Cost:.2f}/{unit}")
            
            # Charts
            col1, col2 = st.columns(2)
            col1.plotly_chart(px.scatter(df, x="Cost", y="Yield", color="Env"), use_container_width=True)
            col2.plotly_chart(px.scatter(df, x="Env", y="Yield", color="Cost"), use_container_width=True)
            
            # Products
            st.subheader("Products")
            products = get_products(best.N*acres, best.P*acres, best.K*acres)
            cols = st.columns(3)
            for i, (name, items) in enumerate(products):
                with cols[i]:
                    st.info(f"**{name}**\n" + "\n".join([f"{n}: {v:.0f}kg" for n,v in items]))

else:  # Water
    st.title("💧 Water Planner")
    
    with st.sidebar:
        crop = st.selectbox("Crop", list(CROPS.keys()))
        unit = st.selectbox("Unit", ["acre", "hectare"])
        area = st.number_input("Area", 0.1, 1000.0, 1.0)
        method = st.selectbox("Method", list(IRRIGATION.keys()))
        per_week = st.selectbox("Per Week", [1, 2, 3], index=1)
        weeks = st.number_input("Weeks", 4, 30, 12)
        rain = st.number_input("Rain (mm/week)", 0.0)
    
    eff = IRRIGATION[method]
    base = CROPS[crop]
    
    # Growth stages
    early = int(weeks * 0.3)
    mid = int(weeks * 0.4)
    late = weeks - early - mid
    kc_values = [0.8]*early + [1.0]*mid + [0.7]*late
    
    schedule = []
    total = 0
    m2 = 4047 if unit == "acre" else 10000
    
    for w, kc in enumerate(kc_values, 1):
        net = max(0, base*kc - rain)
        gross = net / eff
        liters = gross * m2
        total += liters * area / 1000
        schedule.append({"Week": w, "Kc": kc, "L/unit": int(liters), "L/irrig": int(liters/per_week)})
    
    col1, col2 = st.columns(2)
    col1.metric("Total Water", f"{total:,.0f} m³")
    col2.metric("Avg/Irrigation", f"{int(np.mean([s['L/irrig'] for s in schedule])):,.0f} L")
    
    st.dataframe(pd.DataFrame(schedule))
