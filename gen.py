import streamlit as st
from docx import Document
import pandas as pd
import io

# --- 1. Vstupní genetická data ---
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

# --- 2. Vytvoření tabulky (DataFrame) ---
rows = []
for gen, genotypy in data.items():
    for genotyp, hodnoty in genotypy.items():
        rows.append({
            "Gen": gen,
            "Genotyp": genotyp,
            "Klíč": hodnoty["KLÍČ"],
            "Interpretace": hodnoty["INTERPRETACE"]
        })
df = pd.DataFrame(rows)

# --- 3. UI: Nahraj Word šablonu ---
st.title("🧬 Generátor genetické zprávy")

uploaded_template = st.file_uploader("Nahraj šablonu (.docx)", type=["docx"])
if uploaded_template:
    doc = Document(uploaded_template)

    # --- 4. Najdi místo pro vložení tabulky ---
    target_text = "Datum a čas odběru:"
    insert_index = None
    for i, paragraph in enumerate(doc.paragraphs):
        if target_text in paragraph.text:
            insert_index = i + 2  # vloží se pod oddělovací čáru
            break

    if insert_index is not None:
        # --- 5. Vlož tabulku ---
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col

        for _, row in df.iterrows():
            cells = table.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = str(val)

        # Přesun tabulky na správné místo
        tbl = table._element
        body = doc._body._element
        body.remove(tbl)
        doc.paragraphs[insert_index]._element.addnext(tbl)

        # --- 6. Export ---
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        st.download_button(
            label="📄 Stáhnout hotový report",
            data=output,
            file_name="Geneticka_zprava.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("Nepodařilo se najít cílové místo pro vložení tabulky.")



