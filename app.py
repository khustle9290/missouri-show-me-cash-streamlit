import os
import time
import glob
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Streamlit app title
st.title("Missouri Show Me Cash Data Downloader & Cleaner")

st.markdown("""
### Instructions:
1. Click the button below to download the latest **Show Me Cash Excel file** from the Missouri Lottery website.  
2. The file will automatically be renamed to `ShowMeCash.xlsx` in the `data/` folder.  
3. The data will be cleaned (header fixed, extra rows removed).  
4. You can download the cleaned version directly from Streamlit.  

🔗 [Source: Missouri Lottery Show Me Cash](https://www.molottery.com/game/show-me-cash)
""")

# Folder where downloaded + cleaned files will be stored
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def download_file():
    """Download the Show Me Cash Excel file using Selenium headless Chrome."""
    url = "https://www.molottery.com/game/show-me-cash"
    download_dir = os.path.abspath(DATA_DIR)

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    # Click the download button (Excel link)
    try:
        download_button = driver.find_element("xpath", "//a[contains(@href, 'xlsx')]")
        download_button.click()
    except Exception as e:
        st.error(f"Download failed: {e}")
        driver.quit()
        return None

    # Wait for file to appear
    downloaded_file = None
    timeout = 30  # seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        files = glob.glob(os.path.join(download_dir, "*.xlsx"))
        if files:
            latest_file = max(files, key=os.path.getctime)

            # Check if Chrome is still writing (.crdownload present)
            if not latest_file.endswith(".crdownload"):
                downloaded_file = latest_file
                break
        time.sleep(1)

    driver.quit()

    if not downloaded_file:
        st.error("Download did not complete in time.")
        return None

    # Final renamed file path
    final_path = os.path.join(download_dir, "ShowMeCash.xlsx")

    # Remove old file if it exists
    if os.path.exists(final_path):
        os.remove(final_path)

    # Rename safely
    os.rename(downloaded_file, final_path)
    return final_path


def clean_data(file_path):
    """Clean the downloaded Show Me Cash Excel file."""
    df = pd.read_excel(file_path, header=None)

    # Drop first header row
    df = df.drop(index=0)

    # Keep first 6 columns
    df = df.iloc[:, :6]

    # Rename columns
    df.columns = ["Draw Date", "Draw Time", "Numbers As Drawn", 
                  "Numbers In Order", "Jackpot", "Winners"]

    # Save cleaned version
    cleaned_path = os.path.join(DATA_DIR, "showmecash-winning-numbers-cleaned.xlsx")
    df.to_excel(cleaned_path, index=False)

    return df, cleaned_path


# Streamlit button
if st.button("Download & Clean Show Me Cash Data"):
    with st.spinner("Downloading... please wait"):
        file_path = download_file()

    if file_path:
        with st.spinner("Cleaning data..."):
            df, cleaned_file = clean_data(file_path)

        st.success("Data downloaded and cleaned successfully!")
        st.dataframe(df.head())

        # Add download button
        with open(cleaned_file, "rb") as f:
            st.download_button("⬇ Download Cleaned Excel", f, file_name="showmecash-winning-numbers-cleaned.xlsx")
