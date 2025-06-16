import streamlit as st
from docx import Document
import pandas as pd

# Ukázková data
data = [
    {
        "GEN": "MCM6 13910",
        "VARIANTA": "TT",
        "KLÍČ": "+/+",
        "INTERPRETACE": "Vrozená tolerance laktózy. Laktáza se ve střevě tvoří celoživotně. Není potřeba dodržovat bezlaktózovou dietu."
    },
    {
        "GEN": "DAO",
        "VARIANTA": "CT",
        "KLÍČ": "+/-",
        "INTERPRETACE": "Riziko histaminové intolerance spojené s migrénami. Doporučena nízkohistaminová dieta."
    },
    {
        "GEN": "PEMT (rs7946)",
        "VARIANTA": "CT",
        "KLÍČ": "+/-",
        "INTERPRETACE": "Pomalejší odbourávání tuků v játrech. Riziko dysfunkce při nedostatku cholinu."
    }
]

st.title("Genetický výstup – generátor zpráv")

# Zobrazit celou tabulku se všemi záznamy
st.subheader("Seznam genů")
df = pd.DataFrame(data)
st.dataframe(df)

# Textové pole pro zadání genu
gen_input = st.text_input("Zadej název genu (např. DAO):")

if st.button("Generovat zprávu"):
    zaznam = next((z for z in data if z["GEN"].lower() == gen_input.lower()), None)
    if zaznam:
        # Zobrazit detailní data jako tabulku (jeden řádek)
        st.subheader("Detail genetického záznamu")
        st.table(pd.DataFrame([zaznam]))
        
        # Vytvoření Word dokumentu
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        doc.add_paragraph(f"GEN: {zaznam['GEN']}")
        doc.add_paragraph(f"VARIANTA: {zaznam['VARIANTA']}")
        doc.add_paragraph(f"KLÍČ: {zaznam['KLÍČ']}")
        doc.add_paragraph("INTERPRETACE:")
        doc.add_paragraph(zaznam["INTERPRETACE"])
        
        filename = f"{zaznam['GEN'].replace(' ', '_')}_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Gen nebyl nalezen v databázi.")

