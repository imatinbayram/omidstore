<p align="center">
  <img src="logo.png" alt="OMID HESABAT Logo" width="150"/>
</p>

# 📊 OMID HESABAT

**OMID HESABAT** Streamlit tətbiqi mağazalardan stok məlumatlarını API vasitəsilə çəkir və istifadəçiyə tarix və bölgə üzrə interaktiv hesabat təqdim edir.

---

## 🚀 Xüsusiyyətlər

- Bölgə və tarix üzrə filtr
- Hər bir mağaza üçün məlumatların tədrici yüklənməsi
- Progress bar ilə yüklənmə vəziyyəti
- Cəmi məbləğlər və yekun hesabat
- Boş və tapılmayan məlumatlar üçün xəbərdarlıq
- Cədvəl `pandas.DataFrame.style` ilə formatlanır

---

## 📁 Fayllar

| Fayl | Təsviri |
|------|---------|
| `streamlit_app.py` | Əsas Streamlit tətbiqi |
| `StoreInfo.xlsx` | Mağaza kodları və bölgə məlumatları |
| `logo.png` | Tətbiq ikonu |

---

## ⚙️ Quraşdırma

Python 3.9 və ya daha yuxarı tələb olunur.  

```bash
pip install streamlit pandas requests openpyxl
