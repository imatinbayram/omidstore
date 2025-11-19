# streamlit_app.py
import streamlit as st
import pandas as pd
import warnings
import requests
import time

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

b_col, s_col, button_col = st.columns(3, vertical_alignment="bottom")

b_tarix = b_col.date_input("Başlanğıc tarixi", label_visibility="visible")
s_tarix = s_col.date_input("Son tarix", label_visibility="visible", key='tarix2')
show_button = button_col.button("Göstər", use_container_width=True)



if show_button:
    b_tarix_format = b_tarix.isoformat()
    s_tarix_format = s_tarix.isoformat()

    # Read store codes and Bolge from Excel
    store_df = pd.read_excel("Store.xlsx")
    store_df = store_df.dropna(subset=["Kod"])  # boş Kod-ları silirik
    store_codes = store_df["Kod"].astype(str).tolist()
    
    # Bolge üçün dict yarat, tez lookup üçün
    store_bolge_map = dict(zip(store_df["Kod"].astype(str), store_df["Bolge"]))
    
    # Initialize combined DataFrame
    all_data = pd.DataFrame()

    # Placeholders for dynamic updates
    status_placeholder = st.empty()
    table_placeholder = st.empty()
    progress_bar = st.progress(0)

    # -----------------------------
    # FUNCTION TO LOAD DATA
    # -----------------------------
    def stok_hesabat(store_code, tarix_format1, tarix_format2):
        query = f"""
        SELECT * FROM [NewDynCashReportDB].[dbo].[DynCashCekEsasli_MB] ('{tarix_format1}','{tarix_format2}','{store_code}')
        """
        url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        html_json = {"Query": query, "Kod": st.secrets["Kod"]}

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

    # -----------------------------
    # LOOP OVER STORES
    # -----------------------------
    for i, store_code in enumerate(store_codes, start=1):
        status_placeholder.text(f"📊 Məlumatlar yüklənir: {store_code} ({i}/{len(store_codes)})...")

        df = stok_hesabat(store_code, b_tarix_format, s_tarix_format)

        if not df.empty:
            # Add store name column to preserve order
            df["Kod"] = store_code
            df["Bolge"] = store_bolge_map.get(store_code, "Digər")  # Bolge əlavə olunur
            all_data = pd.concat([all_data, df], ignore_index=True)
        
            # Preserve store order from Excel
            stok_cem = (
                all_data.groupby(["Kod", "Bolge", "Mağaza adı"], sort=False)["Yekun məbləğ"]
                .sum()
                .reset_index()
            )
            
            # Ensure order matches Excel order
            stok_cem["Kod"] = pd.Categorical(stok_cem["Kod"], categories=store_codes, ordered=True)
            stok_cem = stok_cem.sort_values("Kod", key=lambda x: x.cat.codes)
            
            #stok_cem.index = np.arange(1, len(stok_cem)+1)
            
            stok_cem = stok_cem.set_index("Bolge")

            styled_stok_cem = (
                stok_cem.style
                .format({"Yekun məbləğ": lambda x: f"{x:,.2f}"})
                .hide(axis="index")
            )
            table_placeholder.table(styled_stok_cem)

        else:
            st.warning(f"⚠️ {store_code} kodlu mağaza üçün məlumat tapılmadı!")

        # Update progress bar
        progress = int((i / len(store_codes)) * 100)
        progress_bar.progress(progress)

        # Small delay for smoother updates
        time.sleep(0.7)

    # Final message
    status_placeholder.text("🎯 Bütün mağaza məlumatları yükləndi!")
    progress_bar.progress(100)


