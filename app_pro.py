# =====================================================
# 💧 Bleb Data Analysis – Professional Edition (Sunrise Glow)
# Developed by Stefanie Puentes Chirivi & Isabel Sofia Bejarano | Universidad de los Andes
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------------
# General configuration
# -----------------------------
st.set_page_config(
    page_title="Bleb Data Analysis – Professional Edition",
    page_icon="💧",
    layout="centered"
)

# Sunrise Glow palette
DARK_BLUE = "#233D4D"
ORANGE = "#FE7F2D"
YELLOW = "#FCCA46"
LIGHT_GREEN = "#A1C181"
TEAL = "#619B8A"

# -----------------------------
# Custom CSS (Fixed and Complete)
# -----------------------------
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(180deg, #ffffff 0%, #f5f9f7 100%);
    color: {DARK_BLUE};
    font-family: 'Lato', sans-serif;
}}
h1, h2, h3 {{
    color: {DARK_BLUE};
    font-weight: 700;
    text-align: center;
}}
hr {{
    border: none;
    border-top: 2px solid {LIGHT_GREEN};
    margin: 25px 0;
}}
.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 900px;
}}

/* --- Fix text color for radio buttons --- */
div[role="radiogroup"] label p {{
    color: #233D4D !important; /* dark blue text */
    font-weight: 500;
}}

/* --- Radio buttons visible on all backgrounds --- */
div[role="radiogroup"] > label > div:first-child {{
    background-color: #FE7F2D !important; /* orange default */
    border: 1.5px solid #233D4D !important;
}}
div[role="radiogroup"] input:checked + div:first-child {{
    background-color: #A1C181 !important; /* green when active */
    border: 1.5px solid #233D4D !important;
}}

/* --- Adjust warning box text for contrast --- */
.stAlert p {{
    color: #233D4D !important; /* dark text for visibility */
    font-weight: 500;
}}
</style>
""", unsafe_allow_html=True)


# -----------------------------
#  Header and description
# -----------------------------
st.title("💧 Bleb Data Analysis – Professional Edition")
st.markdown("""
This tool analyzes *bleb height vs. time* data extracted from **Kinovea (.csv)** files  
to evaluate the stability and retraction dynamics of tissue liftings.

By quantifying height preservation and rate of retraction,  
different **lifting agents** can be compared to assess how long they maintain a stable elevation,  
giving the physician time to operate effectively.
""")

st.markdown("---")

# -----------------------------
# Step 1 – Upload data
# -----------------------------
st.header("Step 1 · Upload your data file")
st.markdown("""
Upload the `.csv` file exported from **Kinovea**, which should contain time (ms)  
and vertical distance measurements between *Point A* and *Point B*.

Before proceeding, ensure the following:
- The **height direction** is consistent (Point A above Point B).  
""")

uploaded_file = st.file_uploader("Upload Kinovea CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=";")
    st.success(f"✅ File `{uploaded_file.name}` uploaded successfully.")

    # Extract relevant columns
    time = df.iloc[:, 0].to_list()
    height_raw = df.iloc[:, 1].to_list()
    reference_value = df.iloc[:, 2].to_list()[0]
    reference_value = float(reference_value.replace(",", "."))
    time_min = [v / 60000 for v in time]
    height_val = [float(str(v).replace(",", ".")) for v in height_raw]
    bleb_height = [v - reference_value for v in height_val]

    # -----------------------------
    #  Step 2 – Height profile
    # -----------------------------
    st.header("Step 2 · Height profile over time")
    st.markdown("""
    The following plot shows **bleb height (mm)** over **time (min)**.  
    A gradual decrease represents normal retraction behavior.  
    A stable or slowly descending curve indicates a lifting agent with good retention capacity.
    """)
    fig1, ax1 = plt.subplots()
    ax1.plot(time_min, bleb_height, color=TEAL, linewidth=2)
    ax1.set_xlabel("Time (min)")
    ax1.set_ylabel("Height (mm)")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    if "time_trimmed" not in st.session_state:
        st.session_state["time_trimmed"] = time_min.copy()
        st.session_state["height_trimmed"] = bleb_height.copy()
        st.session_state["trim_confirmed"] = False
    
    # -----------------------------
    #  Step 3 – Points remotion
    # -----------------------------
    st.header("Step 3 · Points remotion")
    st.markdown("""
    If the plot shows any **noisy or inconsistent points** at the beginning or end of the dataset, you can remove them.

    To do this:
    - Set the number of points to remove **from the start** in the variable `remove_begin`.
    - Set the number of points to remove **from the end** in the variable `remove_last`.
    If your data looks clean and no points need to be removed, **skip the cell below** and move on to the next step.
    """)
    
    #Range slider
    disabled_trim = st.session_state.get("trim_confirmed", False)
    start_idx, end_idx = st.slider(
        "Trim data range",
        min_value=0,
        max_value=len(time_min),
        value=(0, len(time_min)),
        disabled=disabled_trim
    )
    
    if disabled_trim:
        st.info("🔒 Trimming locked. Click 'Reset trimming' to modify.")
    
    # Convert to removal counts
    remove_begin = start_idx
    remove_last = len(time_min) - end_idx
    
    if remove_last == 0:
        time_preview = time_min[remove_begin:]
        height_preview= bleb_height[remove_begin:]
    else:
        time_preview = time_min[start_idx:end_idx]
        height_preview = bleb_height[start_idx:end_idx]
    
    # Visualization
    fig2, ax2 = plt.subplots()
    ax2.plot(time_min, bleb_height, color="lightgray", linestyle="--", label="Original data")
    ax2.plot(time_preview, height_preview, color=TEAL, linewidth=2, label="Trimmed data")
    ax2.set_xlabel("Time (min)")
    ax2.set_ylabel("Height (mm)")
    ax2.set_title("Effect of Removing Points")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

    # Button to confirm trimming
    if st.button("✅ Confirm trimming"):
        st.session_state["time_trimmed"] = time_preview.copy()
        st.session_state["height_trimmed"] = height_preview.copy()
        st.session_state["trim_confirmed"] = True

        st.success(
            f"Trim confirmed: {remove_begin} points removed from start, "
            f"{remove_last} from end."
        )
    
    if st.button("🔄 Reset trimming"):
        st.session_state["trim_confirmed"] = False
        st.session_state["time_trimmed"] = time_min.copy()
        st.session_state["height_trimmed"] = bleb_height.copy()
    
    # -----------------------------
    #  Step 4 – Smoothing
    # -----------------------------
    st.header("Step 4 · Data smoothing")
    st.markdown("""
    A moving-average filter reduces acquisition noise and allows a clearer view of the overall trend.  
    Adjust the window size to control the level of smoothing.
    """)
    
    if not st.session_state["trim_confirmed"]:
        st.warning("Please confirm trimming before applying smoothing.")
        st.stop()

    time_used = st.session_state["time_trimmed"]
    height_used = st.session_state["height_trimmed"]
    
    window_size = st.slider("Smoothing window (points)", 5, 50, 30)
    df_bleb = pd.DataFrame({"time_min": time_used, "height": height_used})
    df_bleb["filtered"] = df_bleb["height"].rolling(window=window_size, center=True).mean()
    df_valid = df_bleb.dropna(subset=["filtered"])

    fig2, ax2 = plt.subplots()
    ax2.plot(df_bleb["time_min"], df_bleb["height"], label="Raw data", color=ORANGE, alpha=0.5)
    ax2.plot(df_valid["time_min"], df_valid["filtered"],
             label=f"Smoothed (window = {window_size})", color=YELLOW, linewidth=2)
    ax2.set_xlabel("Time (min)")
    ax2.set_ylabel("Height (mm)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

    # -----------------------------
    #  Step 5 – Rate of change
    # -----------------------------
    st.header("Step 5 · Rate of height change")
    st.markdown("""
    This plot represents the **rate of height change (dH/dt)** in mm/min.  
    Negative values correspond to retraction.  
    Sudden drops indicate rapid collapse of the bleb, while stable near-zero values indicate sustained elevation.
    """)

    mode = st.radio("Select dataset for calculation:", ["Smoothed", "Raw"])
    if mode == "Smoothed":
        bleb_data = df_valid["filtered"].to_numpy()
        time_data = df_valid["time_min"].to_numpy()
    else:
        bleb_data = df_bleb["height"].to_numpy()
        time_data = df_bleb["time_min"].to_numpy()

    if len(bleb_data) < 2:
        st.warning("⚠️ Not enough valid data points for rate calculation. Try reducing the smoothing window.")
    else:
        rate_change = np.gradient(bleb_data, time_data)
        fig3, ax3 = plt.subplots()
        ax3.plot(time_data, rate_change, color=DARK_BLUE, linewidth=2)
        ax3.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax3.set_xlabel("Time (min)")
        ax3.set_ylabel("Rate of change (mm/min)")
        ax3.set_title("Rate of Height Change")
        ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)
        
        # Basic metric: total height drop
        drop = bleb_data[0] - bleb_data[-1]
        rate_mean = np.mean(rate_change)
        st.markdown(f"""
        **Total height decrease:** {drop:.2f} mm  
        **Mean bleb velocity:** {rate_mean:.3f} mm/min
        """)

    # -----------------------------
    #  Step 6 – Export
    # -----------------------------
    st.header("Step 6 · Export results")
    st.markdown("Export the processed data for further analysis or record keeping.")
    if len(bleb_data) >= 2:
        output_df = pd.DataFrame({
                    "Time (min)": time_data,
                    "Height (mm)": bleb_data,
                    "Rate of change (mm/min)": rate_change,
                    "Mean bleb velocity (mm/min)": rate_mean
                    })
        buffer = BytesIO()
        output_df.to_excel(buffer, index=False)
        st.download_button(
            label="⬇️ Download Results (Excel)",
            data=buffer.getvalue(),
            file_name=f"{uploaded_file.name.replace('.csv','')}_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Upload a Kinovea CSV file to begin.")