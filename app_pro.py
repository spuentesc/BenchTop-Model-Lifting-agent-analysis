
# =====================================================
# 💧 Bleb Data Analysis – Professional Edition (Sunrise Glow)
# Developed by Stefanie Puentes Chirivi | Universidad de los Andes
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

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
</style>
""", unsafe_allow_html=True)

st.title("💧 Bleb Data Analysis – Professional Edition")
st.markdown("""
This tool analyzes *bleb height vs. time* data extracted from **Kinovea (.csv)** files  
to evaluate the stability and retraction dynamics of tissue liftings.
""")

uploaded_file = st.file_uploader("Upload Kinovea CSV", type="csv")
reference_value = st.number_input("Enter reference height (mm)", min_value=0.0, step=0.1)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ File `{uploaded_file.name}` uploaded successfully.")

    time = df.iloc[:, 0].to_list()
    height_raw = df.iloc[:, 1].to_list()
    time_min = [v / 60000 for v in time]
    height_val = [float(str(v).replace(",", ".")) for v in height_raw]
    bleb_height = [v - reference_value for v in height_val]

    st.header("Height profile over time")
    fig1, ax1 = plt.subplots()
    ax1.plot(time_min, bleb_height, color=TEAL, linewidth=2)
    ax1.set_xlabel("Time (min)")
    ax1.set_ylabel("Height (mm)")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    st.header("Smoothing and rate of change")
    window_size = st.slider("Smoothing window (points)", 5, 100, 30)
    df_bleb = pd.DataFrame({"time_min": time_min, "height": bleb_height})
    df_bleb["filtered"] = df_bleb["height"].rolling(window=window_size, center=True).mean()
    df_valid = df_bleb.dropna(subset=["filtered"])

    fig2, ax2 = plt.subplots()
    ax2.plot(df_bleb["time_min"], df_bleb["height"], label="Raw", color=ORANGE, alpha=0.5)
    ax2.plot(df_valid["time_min"], df_valid["filtered"], label=f"Smoothed (window={window_size})", color=YELLOW, linewidth=2)
    ax2.legend(); ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

    mode = st.radio("Select dataset for calculation:", ["Smoothed", "Raw"])
    if mode == "Smoothed":
        bleb_data = df_valid["filtered"].to_numpy()
        time_data = df_valid["time_min"].to_numpy()
    else:
        bleb_data = df_bleb["height"].to_numpy()
        time_data = df_bleb["time_min"].to_numpy()

    if len(bleb_data) < 2:
        st.warning("⚠️ Not enough valid data points for rate calculation.")
    else:
        rate_change = np.gradient(bleb_data, time_data)
        fig3, ax3 = plt.subplots()
        ax3.plot(time_data, rate_change, color=DARK_BLUE, linewidth=2)
        ax3.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax3.set_xlabel("Time (min)")
        ax3.set_ylabel("Rate of change (mm/min)")
        st.pyplot(fig3)

        drop = bleb_data[0] - bleb_data[-1]
        duration = time_data[-1] - time_data[0]
        rate_mean = drop / duration if duration != 0 else 0
        st.markdown(f"**Total height decrease:** {drop:.2f} mm  
**Mean retraction rate:** {rate_mean:.3f} mm/min")

        output_df = pd.DataFrame({
            "Time (min)": time_data,
            "Height (mm)": bleb_data,
            "Rate of change (mm/min)": rate_change
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
