import os
import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Paths
download_path = os.path.join(os.getcwd(), "data")
os.makedirs(download_path, exist_ok=True)

final_filename = "ShowMeCash.xlsx"
final_path = os.path.join(download_path, final_filename)
cleaned_path = os.path.join(download_path, "showmecash-winning-numbers-cleaned.xlsx")

# ChromeDriver path (update this if your chromedriver.exe is in another location)
webdriver_path = r"C:\Users\vin\Downloads\chromedriver.exe"

# URL
url = "https://www.molottery.com/show-me-cash/past-winning-numbers.jsp"

def download_file():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--headless")  # remove if you want to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    try:
        download_link = driver.find_element(By.ID, "excelDl")
        download_link.click()
        st.info("Download initiated...")
        time.sleep(10)  # wait for download
        driver.quit()
    except Exception as e:
        st.error(f"Download failed: {e}")
        driver.quit()
        return None

    # Find latest downloaded file
    files = [f for f in os.listdir(download_path) if f.endswith('.xlsx')]
    files.sort(key=lambda f: os.path.getctime(os.path.join(download_path, f)), reverse=True)
    if not files:
        st.error("No file found in download folder.")
        return None

    latest_file = os.path.join(download_path, files[0])
    os.rename(latest_file, final_path)
    return final_path

def process_file(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.iloc[1:]
        df = df.iloc[:, :6]
        df.columns = ['Draw Date', 'Draw Time', 'Numbers As Drawn', 'Numbers In Order', 'Jackpot', 'Winners']
        df.to_excel(cleaned_path, index=False)
        st.success(f"Cleaned file saved to: {cleaned_path}")
        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# --- Streamlit UI ---
st.title("🎰 Missouri Show Me Cash Downloader (Selenium Version)")

st.markdown("""
### 📖 How to Use
1. Make sure you have **Google Chrome** installed and that your `chromedriver.exe` path is correct.  
2. Click the **Download & Clean Latest File** button below.  
3. The program will fetch the latest Show Me Cash Excel file from the [Missouri Lottery Website](https://www.molottery.com/show-me-cash/past-winning-numbers.jsp).  
4. The file will be automatically renamed to `ShowMeCash.xlsx` inside the **data/** folder.  
5. A cleaned version will be saved as `showmecash-winning-numbers-cleaned.xlsx`.  
6. You can preview the cleaned results directly in this app.  
7. Optionally, click **Download Cleaned Excel** to save it to your computer.  
---
""")

if st.button("⬇️ Download & Clean Latest File"):
    st.info("Downloading file...")
    file_path = download_file()
    if file_path:
        st.info("Processing file...")
        df = process_file(file_path)
        if df is not None:
            st.dataframe(df)
            # Download button
            with open(cleaned_path, "rb") as f:
                st.download_button(
                    label="📥 Download Cleaned Excel",
                    data=f,
                    file_name="showmecash-winning-numbers-cleaned.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
