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

        # Spočítáme celkový počet řádků (součet počtu variant pro všechny geny)
        total_rows = sum(len(v) for v in vybrane.values()) + 1
        table = doc.add_table(rows=total_rows, cols=4)
        table.style = 'Light List Accent 1'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "GEN"
        hdr_cells[1].text = "VARIANTA"
        hdr_cells[2].text = "KLÍČ"
        hdr_cells[3].text = "INTERPRETACE"

        row_idx = 1
        for gen, varianty in vybrane.items():
            first_row = True
            for var in varianty:
                row_cells = table.rows[row_idx].cells
                if first_row:
                    row_cells[0].text = gen
                    first_row = False
                else:
                    row_cells[0].text = ""  # ostatní řádky GEN necháme prázdné

                row_cells[1].text = var
                row_cells[2].text = data[gen][var]["KLÍČ"]
                row_cells[3].text = data[gen][var]["INTERPRETACE"]

                row_idx += 1

        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Nezaškrtl jsi žádný gen ani variantu.")


