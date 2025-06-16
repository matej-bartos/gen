import streamlit as st
from docx import Document

# Data: gen -> varianta -> klíč + interpretace
data = {
    "MCM6 13910": {
        "TT": {"KLÍČ": "+/+", "INTERPRETACE": "Vrozená tolerance laktózy."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Částečná tolerance laktózy."},
        "CC": {"KLÍČ": "-/-", "INTERPRETACE": "Nedostatek laktázy."}
    },
    "DAO": {
        "CC": {"KLÍČ": "+/+", "INTERPRETACE": "Normální aktivita DAO."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Riziko histaminové intolerance."},
        "TT": {"KLÍČ": "-/-", "INTERPRETACE": "Nízká aktivita DAO."}
    },
    "PEMT (rs7946)": {
        "CC": {"KLÍČ": "+/+", "INTERPRETACE": "Normální metabolismus tuků."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Pomalejší odbourávání tuků."},
        "TT": {"KLÍČ": "-/-", "INTERPRETACE": "Výrazně snížený metabolismus tuků."}
    }
}

st.title("Genetický výstup – generátor zpráv")

vybrane_data = []

for gen in data.keys():
    if st.checkbox(gen):
        varianty = st.multiselect(f"Vyber varianty pro {gen}:", options=list(data[gen].keys()), key=gen)
        for var in varianty:
            klic = data[gen][var]["KLÍČ"]
            interpretace = data[gen][var]["INTERPRETACE"]
            st.write(f"**{gen} - Varianta {var}**")
            st.write(f"Klíč: {klic}")
            st.write(f"Interpretace: {interpretace}\n")
            vybrane_data.append({
                "GEN": gen,
                "VARIANTA": var,
                "KLÍČ": klic,
                "INTERPRETACE": interpretace
            })

if st.button("Generovat zprávu"):
    if vybrane_data:
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        table = doc.add_table(rows=len(vybrane_data)+1, cols=4)
        table.style = 'Light List Accent 1'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "GEN"
        hdr_cells[1].text = "VARIANTA"
        hdr_cells[2].text = "KLÍČ"
        hdr_cells[3].text = "INTERPRETACE"

        for i, zaznam in enumerate(vybrane_data, start=1):
            row_cells = table.rows[i].cells
            row_cells[0].text = zaznam["GEN"]
            row_cells[1].text = zaznam["VARIANTA"]
            row_cells[2].text = zaznam["KLÍČ"]
            row_cells[3].text = zaznam["INTERPRETACE"]

        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Nezaškrtl jsi žádný gen ani variantu.")
