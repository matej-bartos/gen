import streamlit as st
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

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

def merge_cells_vertically(table, col_idx, start_row_idx, end_row_idx):
    """Sloučí buňky ve sloupci col_idx od start_row_idx do end_row_idx (včetně) vertikálně."""
    first_cell = table.cell(start_row_idx, col_idx)
    for row in range(start_row_idx + 1, end_row_idx + 1):
        cell_to_merge = table.cell(row, col_idx)
        first_cell.merge(cell_to_merge)

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
            start_merge_idx = row_idx
            for var in varianty:
                row_cells = table.rows[row_idx].cells
                row_cells[1].text = var
                row_cells[2].text = data[gen][var]["KLÍČ"]
                row_cells[3].text = data[gen][var]["INTERPRETACE"]
                row_idx += 1
            # Sloučíme buňky GEN ve sloupci 0 přes všechny varianty
            merge_cells_vertically(table, 0, start_merge_idx, row_idx - 1)
            # Do první sloučené buňky dáme jméno genu
            table.cell(start_merge_idx, 0).text = gen

        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Nezaškrtl jsi žádný gen ani variantu.")


