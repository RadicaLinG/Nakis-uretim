import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Veritabanı Fonksiyonu
def veri_hazirla():
    conn = sqlite3.connect('nakis.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS uretim 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tarih TEXT, personel TEXT, vardiya TEXT, 
                  makine TEXT, is_emri TEXT, vurus INTEGER)''')
    conn.commit()
    conn.close()

veri_hazirla()

# Menü Seçimi
menu = st.sidebar.selectbox("Menü", ["Kayıt Girişi", "Yönetici Paneli"])

if menu == "Kayıt Girişi":
    st.header("🧵 Üretim Giriş Ekranı")
    
    personel = st.selectbox("Personel", ["Ahmet", "Mehmet", "Ayşe", "Fatma"])
    makine = st.selectbox("Makine", [f"Makine {i}" for i in range(1, 15)])
    is_emri = st.text_input("İş Emri No")
    vurus = st.number_input("Vuruş Sayısı", min_value=0, step=100)

    if st.button("Sisteme Kaydet"):
        if is_emri != "":
            conn = sqlite3.connect('nakis.db')
            c = conn.cursor()
            tarih = datetime.now().strftime("%d-%m-%Y %H:%M")
            c.execute("INSERT INTO uretim (tarih, personel, makine, is_emri, vurus) VALUES (?,?,?,?,?)",
                      (tarih, personel, makine, is_emri, vurus))
            conn.commit()
            conn.close()
            st.success("Kayıt başarıyla eklendi!")
        else:
            st.warning("Lütfen iş emri numarasını girin.")

else:
    st.header("📊 Yönetici İzleme Paneli")
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "1234":
        conn = sqlite3.connect('nakis.db')
        df = pd.read_sql_query("SELECT * FROM uretim", conn)
        conn.close()
        
        if not df.empty:
            st.write("### Güncel Üretim Listesi")
            st.dataframe(df)
            
            # Excel için basit CSV indirici
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Dosyayı İndir (CSV)", csv, "uretim.csv", "text/csv")
        else:
            st.info("Henüz hiç kayıt yapılmamış.")
