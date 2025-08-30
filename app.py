import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Streamlit UI ---
st.title("Missouri Show Me Cash - Data Downloader")

st.write("This app downloads the latest Show Me Cash numbers from [lotteryusa.com](https://www.lotteryusa.com/missouri/)")

# --- Scraping function ---
def scrape_show_me_cash():
    url = "https://www.lotteryusa.com/missouri/show-me-cash/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    rows = soup.select("li.draw-result")

    for row in rows:
        date_elem = row.select_one(".draw-date")
        nums = row.select(".draw-result li")

        if not date_elem or not nums:
            continue

        draw_date = date_elem.get_text(strip=True)
        numbers = [n.get_text(strip=True) for n in nums[:5]]

        if len(numbers) == 5:
            data.append([draw_date] + numbers)

    df = pd.DataFrame(data, columns=["Draw Date", "Num1", "Num2", "Num3", "Num4", "Num5"])
    return df

# --- Main logic ---
if st.button("Fetch Latest Data"):
    df = scrape_show_me_cash()
    
    if not df.empty:
        st.success("✅ Latest Show Me Cash data downloaded!")
        st.dataframe(df)

        # Add sum column
        df["Sum"] = df[["Num1", "Num2", "Num3", "Num4", "Num5"]].astype(int).sum(axis=1)

        # Allow download as Excel
        excel_file = "show_me_cash_data.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button("📥 Download Excel File", f, file_name=excel_file)
    else:
        st.error("⚠️ No data found. Website may have changed.")

# --- Example of file format for uploads ---
st.subheader("📂 Example of File Format")
st.write("If you want to upload your own dataset, it should look like this:")

example_data = {
    "Draw Date": ["25-Aug-25", "24-Aug-25", "23-Aug-25"],
    "Num1": [19, 4, 8],
    "Num2": [24, 6, 11],
    "Num3": [27, 10, 29],
    "Num4": [33, 13, 32],
    "Num5": [35, 29, 38],
}
st.dataframe(pd.DataFrame(example_data))
