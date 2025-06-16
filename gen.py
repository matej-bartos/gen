import streamlit as st
from docx import Document

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

vybrane = {}

for gen in data.keys():
    if st.checkbox(gen):
        varianty = st.multiselect(f"Vyber varianty pro {gen}:", options=list(data[gen].keys()), key=gen)
        if varianty:
            vybrane[gen] = varianty
            for var in varianty:
                st.write(f"**{gen} - Varianta {var}**")
                st.write(f"Klíč: {data[gen][var]['KLÍČ']}")
                st.write(f"Interpretace: {data[gen][var]['INTERPRETACE']}\n")

if st.button("Generovat zprávu"):
    if vybrane:
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        table = doc.add_table(rows=len(vybrane)+1, cols=4)
        table.style = 'Light List Accent 1'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "GEN"
        hdr_cells[1].text = "VARIANTA"
        hdr_cells[2].text = "KLÍČ"
        hdr_cells[3].text = "INTERPRETACE"

        for i, (gen, varianty) in enumerate(vybrane.items(), start=1):
            klice = []
            interpretace = []
            for var in varianty:
                klice.append(data[gen][var]["KLÍČ"])
                interpretace.append(data[gen][var]["INTERPRETACE"])

            row_cells = table.rows[i].cells
            row_cells[0].text = gen
            row_cells[1].text = ", ".join(varianty)
            row_cells[2].text = ", ".join(klice)
            # Interpretace na nové řádky, proto použijeme '\n' a pak při uložení Word to automaticky převede na nový řádek
            row_cells[3].text = "\n\n".join(interpretace)

        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Nezaškrtl jsi žádný gen ani variantu.")

