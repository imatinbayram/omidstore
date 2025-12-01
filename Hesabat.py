# streamlit_app.py
import streamlit as st
import pandas as pd
import warnings
import requests
import time
from datetime import date

warnings.simplefilter("ignore")

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(
    page_title='OMID HESABAT',
    page_icon='logo.png',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "# OMID HESABAT \n Bu hesabat OMID üçün hazırlanmışdır."}
)

# Read store codes and Bolge from Excel
store_df = pd.read_excel("StoreInfo.xlsx")
store_df = store_df.dropna(subset=["Kod"])
bolgeler = store_df["Bolge"].astype(str).unique().tolist()

bugun_tarix = date.today()
tarix_ilk = bugun_tarix.replace(day=1).isoformat()
tarix_bugun = bugun_tarix.isoformat()

bolge = st.multiselect(
    "Bölgə seçin",
    options=bolgeler,
    placeholder=""
)

b_col, s_col, button_col = st.columns(3, vertical_alignment="bottom")

b_tarix = b_col.date_input("Başlanğıc tarixi", label_visibility="visible",
                           value = bugun_tarix.replace(day=1))
s_tarix = s_col.date_input("Son tarix", label_visibility="visible", key='tarix2',
                           value = bugun_tarix)
show_button = button_col.button("Göstər", use_container_width=True)

store_df = store_df[store_df["Bolge"]==bolge]

if show_button:
    b_tarix_format = b_tarix.isoformat()
    s_tarix_format = s_tarix.isoformat()

    all_data = pd.DataFrame()
    store_codes = store_df["Kod"].astype(str).tolist()

    table_placeholder = st.empty()
    progress_bar = st.progress(0)

    def stok_hesabat(store_code, tarix_format1, tarix_format2):
        query = f"""
        SELECT * FROM [NewDynCashReportDB].[dbo].[DynCashCekEsasli] ('{tarix_format1}','{tarix_format2}','{store_code}')
        UNION ALL
        SELECT * FROM [NewDynCashReportDB].[dbo].[MikroCekEsasli] ('{tarix_format1}','{tarix_format2}','{store_code}')
        """
        url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        html_json = {"Query": query, "Kod": "B!Q"}

        response = requests.get(url, json=html_json, headers=headers, verify=False)
        if response.status_code == 200:
            api_data = response.json()
            if api_data["Code"] == 0:
                return pd.DataFrame(api_data["Data"])
            else:
                st.warning(f"API Error ({store_code}): {api_data['Message']}")
                return pd.DataFrame()
        else:
            st.error(f"HTTP Error ({store_code}): {response.status_code} {response.text}")
            return pd.DataFrame()

    for i, store_code in enumerate(store_codes, start=1):
        st.text(f"📊 ({i}/{len(store_codes)}) Məlumatlar yüklənir: {store_code} - {store_df[store_df['Kod']==int(store_code)]['Ad'].iloc[0]}")
        df = stok_hesabat(store_code, b_tarix_format, s_tarix_format)

        if not df.empty:
            df["Kod"] = store_code
            df["Bolge"] = bolge
            all_data = pd.concat([all_data, df], ignore_index=True)
        
            stok_cem = (
                all_data.groupby(["Kod", "Bolge", "Mağaza adı"], sort=False)["Yekun məbləğ"]
                .sum()
                .reset_index()
            )
            
            
            stok_cem = stok_cem.set_index("Bolge")
            
            # CƏM
            total_value = stok_cem["Yekun məbləğ"].sum()
            
            cem_setri = pd.DataFrame({
                "Kod": [""],
                "Mağaza adı": ["CƏM"],
                "Yekun məbləğ": [total_value]
            }, index=[""])
            
            stok_cem_setri = pd.concat([stok_cem, cem_setri])

            styled_stok_cem = (
                stok_cem_setri.style
                .format({"Yekun məbləğ": lambda x: f"{x:,.2f}"})
                .hide(axis="index")
            )
            
            table_placeholder.table(styled_stok_cem)

        else:
            st.warning(f"⚠️ {store_code} kodlu mağaza üçün məlumat tapılmadı!")

        
        progress = int((i / len(store_codes)) * 100)
        progress_bar.progress(progress)

        
        time.sleep(0.7)

    progress_bar.progress(100)





