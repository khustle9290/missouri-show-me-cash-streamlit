import os
import pandas as pd
import streamlit as st
import requests

# --- Paths ---
download_path = os.path.join(os.getcwd(), "data")
os.makedirs(download_path, exist_ok=True)

final_filename = "ShowMeCash.xlsx"
final_path = os.path.join(download_path, final_filename)
cleaned_path = os.path.join(download_path, "showmecash-winning-numbers-cleaned.xlsx")

# --- URL ---
url = "https://www.molottery.com/export/sites/missouri/Games/show-me-cash/ShowMeCashPastWinningNumbers.xlsx"

# --- Functions ---
def download_file():
    # Delete old files if exist
    if os.path.exists(final_path):
        os.remove(final_path)
    if os.path.exists(cleaned_path):
        os.remove(cleaned_path)

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(final_path, "wb") as f:
            f.write(response.content)
        st.success(f"Downloaded latest file to {final_path}")
        return final_path
    except Exception as e:
        st.error(f"Download failed: {e}")
        return None

def process_file(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.iloc[1:]           # remove first row
        df = df.iloc[:, :6]        # first 6 columns
        df.columns = ['Draw Date', 'Draw Time', 'Numbers As Drawn', 'Numbers In Order', 'Jackpot', 'Winners']
        df.to_excel(cleaned_path, index=False)
        st.success(f"Cleaned file saved to: {cleaned_path}")
        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# --- Streamlit UI ---
st.title("🎰 Missouri Show Me Cash Downloader (Requests Version)")

st.markdown("""
### 📖 Instructions
1. Old files will be automatically deleted before downloading a new file.
2. Click the **Download & Clean Latest File** button.
3. Preview the cleaned data in the table.
4. Optionally, click **Download Cleaned Excel** to save it locally.
---
""")

if st.button("⬇️ Download & Clean Latest File"):
    file_path = download_file()
    if file_path:
        df = process_file(file_path)
        if df is not None:
            st.dataframe(df)
            with open(cleaned_path, "rb") as f:
                st.download_button(
                    label="📥 Download Cleaned Excel",
                    data=f,
                    file_name="showmecash-winning-numbers-cleaned.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
