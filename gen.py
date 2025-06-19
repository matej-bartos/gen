import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
import io

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Data
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

# Funkce pro přesné vložení tabulky místo placeholderu
def vloz_tabulku_na_misto(doc, vybrane):
    body = doc._body._element
    for i, paragraph in enumerate(doc.paragraphs):
        if '###TABULKA###' in paragraph.text:
            p_element = paragraph._element

            # Vytvoř novou tabulku
            tbl = doc.add_table(rows=1, cols=4)
            tbl.style = 'Table Grid'
            tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

            hdr = tbl.rows[0].cells
            hdr[0].text = "GEN"
            hdr[1].text = "VÝSLEDNÁ VARIANTA"
            hdr[2].text = "Dle klíče"
            hdr[3].text = "INTERPRETACE"

            for gen, varianty in vybrane.items():
                for var in varianty:
                    row = tbl.add_row().cells
                    row[0].text = gen
                    row[1].text = var
                    row[2].text = data[gen][var]["KLÍČ"]
                    row[3].text = data[gen][var]["INTERPRETACE"]

            # Vložit tabulku na místo původního odstavce
            body.insert(body.index(p_element), tbl._element)
            body.remove(p_element)
            break

# Streamlit UI
st.title("🧬 Generátor genetické zprávy")

vybrane = {}
for gen in data:
    if st.checkbox(gen):
        varianty = st.multiselect(f"Varianty pro {gen}:", list(data[gen].keys()), key=gen)
        if varianty:
            vybrane[gen] = varianty

if st.button("📄 Generovat zprávu"):
    if vybrane:
        try:
            doc = Document("Výsledková zpráva.docx")
            vloz_tabulku_na_misto(doc, vybrane)

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="⬇️ Stáhnout výsledkovou zprávu",
                data=buffer,
                file_name="geneticka_zprava.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Nastala chyba při generování zprávy: {e}")
    else:
        st.warning("Vyber alespoň jeden gen.")
