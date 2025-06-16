import streamlit as st
from docx import Document

# Ukázková data - varianta, klíč a interpretace závisí na variantě
data = {
    "MCM6 13910": {
        "TT": {"KLÍČ": "+/+", "INTERPRETACE": "Vrozená tolerance laktózy. Laktáza se ve střevě tvoří celoživotně. Není potřeba dodržovat bezlaktózovou dietu."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Částečná tolerance laktózy."},
        "CC": {"KLÍČ": "-/-", "INTERPRETACE": "Nedostatek laktázy, doporučena bezlaktózová dieta."}
    },
    "DAO": {
        "CC": {"KLÍČ": "+/+", "INTERPRETACE": "Normální aktivita DAO."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Riziko histaminové intolerance spojené s migrénami. Doporučena nízkohistaminová dieta."},
        "TT": {"KLÍČ": "-/-", "INTERPRETACE": "Nízká aktivita DAO, vysoké riziko intolerance."}
    },
    "PEMT (rs7946)": {
        "CC": {"KLÍČ": "+/+", "INTERPRETACE": "Normální metabolismus tuků."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Pomalejší odbourávání tuků v játrech. Riziko dysfunkce při nedostatku cholinu."},
        "TT": {"KLÍČ": "-/-", "INTERPRETACE": "Výrazně snížený metabolismus tuků."}
    }
}

st.title("Genetický výstup – generátor zpráv")

vybrane_geny = {}

# Pro každý gen zobraz checkbox a pokud je zaškrtnutý, nabídni variantu k výběru
for gen in data.keys():
    if st.checkbox(gen):
        varianta = st.selectbox(f"Vyber variantu pro {gen}:", options=list(data[gen].keys()), key=gen)
        klic = data[gen][varianta]["KLÍČ"]
        interpretace = data[gen][varianta]["INTERPRETACE"]
        vybrane_geny[gen] = {
            "VARIANTA": varianta,
            "KLÍČ": klic,
            "INTERPRETACE": interpretace
        }
        st.write(f"**Klíč:** {klic}")
        st.write(f"**Interpretace:** {interpretace}")

if st.button("Generovat zprávu"):
    if vybrane_geny:
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        table = doc.add_table(rows=len(vybrane_geny)+1, cols=4)
        table.style = 'Light List Accent 1'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "GEN"
        hdr_cells[1].text = "VARIANTA"
        hdr_cells[2].text = "KLÍČ"
        hdr_cells[3].text = "INTERPRETACE"

        for i, (gen, info) in enumerate(vybrane_geny.items(), start=1):
            row_cells = table.rows[i].cells
            row_cells[0].text = gen
            row_cells[1].text = info["VARIANTA"]
            row_cells[2].text = info["KLÍČ"]
            row_cells[3].text = info["INTERPRETACE"]

        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Nezaškrtl jsi žádný gen.")
