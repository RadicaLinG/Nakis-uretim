import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# --- SAYFA AYARLARI (ARTIK EN ÜSTTE) ---
st.set_page_config(page_title="Nakış Takip Pro", page_layout="wide")

# --- VERİTABANI AYARLARI ---
def veri_hazirla():
    conn = sqlite3.connect('nakis_uretim.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS uretim 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tarih TEXT, personel TEXT, vardiya TEXT, 
                  makine TEXT, is_emri TEXT, vurus INTEGER, kasnak INTEGER)''')
    conn.commit()
    conn.close()

veri_hazirla()

# --- NAVİGASYON ---
sayfa = st.sidebar.selectbox("Bölüm Seçin", ["Veri Girişi (Personel)", "Yönetim Paneli (Admin)"])

# --- 1. BÖLÜM: PERSONEL VERİ GİRİŞİ ---
if sayfa == "Veri Girişi (Personel)":
    st.title("🧵 Nakış Üretim Kayıt Ekranı")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            personel = st.selectbox("Sorumlu Personel", ["Ahmet", "Mehmet", "Ayşe", "Fatma"])
            vardiya = st.radio("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
            makine_no = st.selectbox("Makine No", [f"Makine {i}" for i in range(1, 15)])
        
        with col2:
            is_emri = st.text_input("İş Emri No / Barkod")
            vurus_sayisi = st.number_input("Toplam Vuruş Sayısı", min_value=0, step=100)
            kasnak_sayisi = st.number_input("Atılan Kasnak Sayısı", min_value=0, step=1)

    if st.button("KAYDI SİSTEME GÖNDER", use_container_width=True):
        if is_emri and vurus_sayisi > 0:
            conn = sqlite3.connect('nakis_uretim.db')
            c = conn.cursor()
            simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO uretim (tarih, personel, vardiya, makine, is_emri, vurus, kasnak) VALUES (?,?,?,?,?,?,?)",
                      (simdi, personel, vardiya, makine_no, is_emri, vurus_sayisi, kasnak_sayisi))
            conn.commit()
            conn.close()
            st.success(f"✅ Kayıt Başarılı! {makine_no} - {vurus_sayisi} Vuruş")
            st.balloons()
        else:
            st.error("Lütfen tüm alanları doldurun!")

# --- 2. BÖLÜM: YÖNETİM PANELİ (ŞİFRELİ) ---
elif sayfa == "Yönetim Paneli (Admin)":
    st.title("📊 Yönetim ve Analiz Paneli")
    
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "1234":
        st.sidebar.success("Erişim Onaylandı")
        
        conn = sqlite3.connect('nakis_uretim.db')
        df = pd.read_sql_query("SELECT * FROM uretim", conn)
        conn.close()

        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Vuruş", f"{df['vurus'].sum():,}")
            c2.metric("Toplam Kasnak", df['kasnak'].sum())
            c3.metric("Kayıt Sayısı", len(df))

            st.subheader("📈 Makine Bazlı Üretim Performansı")
            fig = px.bar(df, x='makine', y='vurus', color='personel', title="Makine ve Personel Dağılımı")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Tüm Kayıtlar")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Excel/CSV Olarak İndir", csv, "uretim_raporu.csv", "text/csv")
        else:
            st.info("Henüz kayıt bulunamadı.")
    elif sifre != "":
        st.error("Hatalı Şifre!")
