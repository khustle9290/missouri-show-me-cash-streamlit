import os
import shutil
import requests
import pandas as pd
import streamlit as st

# ===============================================================
# Missouri Show Me Cash Streamlit App
# ---------------------------------------------------------------
# Instructions:
# 1. This app downloads the official Missouri Lottery "Show Me Cash"
#    past winning numbers file directly from the lottery website.
# 2. The file is saved into a local "data" folder.
# 3. The app will then load and display the historical data.
# 4. Each time you run the app, it re-downloads the latest version.
#
# Run the app:
#   streamlit run app.py
# ===============================================================

DOWNLOAD_URL = "https://www.molottery.com/sites/default/files/DrawGamePastWinningNumbers/ShowMeCashPastWinningNumbers.xlsx"
SAVE_DIR = "data"
FINAL_FILENAME = "showmecash-winning-numbers-cleaned.xlsx"


def download_file():
    """Download the Show Me Cash Excel file and move it into the data folder safely."""
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)

        # Download raw file
        response = requests.get(DOWNLOAD_URL, timeout=15)
        response.raise_for_status()  # raise error if download failed

        raw_path = os.path.join(SAVE_DIR, "showmecash-latest.xlsx")
        with open(raw_path, "wb") as f:
            f.write(response.content)

        # Define final cleaned path
        final_path = os.path.join(SAVE_DIR, FINAL_FILENAME)

        # Move file safely (avoids Windows rename issues)
        shutil.move(raw_path, final_path)

        return final_path

    except Exception as e:
        st.error(f"❌ File download failed: {e}")
        return None


def load_data(file_path):
    """Load the Excel file into a Pandas DataFrame."""
    try:
        df = pd.read_excel(file_path)

        # Normalize column names (sometimes the file may have slight changes)
        df.columns = [col.strip() for col in df.columns]

        return df
    except Exception as e:
        st.error(f"❌ Failed to load data from Excel: {e}")
        return None


# ======================
# Streamlit App UI
# ======================
st.set_page_config(page_title="Missouri Show Me Cash Analyzer", layout="wide")
st.title("🎰 Missouri Show Me Cash - Winning Numbers")

st.write("This app downloads the **latest historical Show Me Cash winning numbers** "
         "directly from the Missouri Lottery website and displays them here.")

# Download + load
file_path = download_file()
if file_path:
    df = load_data(file_path)

    if df is not None:
        st.success("✅ Data downloaded and loaded successfully!")

        # Show preview
        st.subheader("Data Preview")
        st.dataframe(df.head(20))

        # Basic stats
        st.subheader("Quick Stats")
        st.write(f"Total Draws: **{len(df)}**")
        st.write("Date Range: **{} → {}**".format(df['Draw Date'].min(), df['Draw Date'].max()))

        # Frequency table for numbers
        number_cols = [col for col in df.columns if col.startswith("Num")]
        if number_cols:
            all_numbers = df[number_cols].values.flatten()
            freq = pd.Series(all_numbers).value_counts().sort_index()

            st.subheader("Number Frequencies")
            st.bar_chart(freq)

    else:
        st.warning("⚠️ No data to display.")
else:
    st.warning("⚠️ Could not download the file. Check your internet connection.")
