import streamlit as st
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
import io

data = {
    "MCM6 13910": {
        "TT": {"KLÍČ": "+/+", "INTERPRETACE": "Vrozená tolerance laktózy."},
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Částečná tolerance laktózy."},
        "CC": {"KLÍČ": "-/-", "INTERPRETACE": "Nedostatek laktázy."}
    },
    "DAO": {
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Riziko histaminové intolerance."}
    },
    "PEMT (rs7946)": {
        "CT": {"KLÍČ": "+/-", "INTERPRETACE": "Pomalejší odbourávání tuků."}
    }
}

def vloz_tabulku_presne(doc, vybrane):
    body = doc._element.body
    for para in doc.paragraphs:
        if "###TABULKA###" in para.text:
            # Index aktuálního odstavce
            idx = list(body).index(para._element)

            # Odebrat placeholder
            body.remove(para._element)

            # Vytvořit tabulku
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
            body.insert(idx, tbl._element)
            break

st.title("🧬 Generátor genetické zprávy")

vybrane = {}
for gen in data:
    if st.checkbox(gen):
        varianty = st.multiselect(f"Varianty pro {gen}:", list(data[gen].keys()), key=gen)
        if varianty:
            vybrane[gen] = varianty

if st.button("📄 Generovat zprávu"):
    if vybrane:
        doc = Document("Výsledková zpráva.docx")
        vloz_tabulku_presne(doc, vybrane)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Stáhnout zprávu",
            data=buffer,
            file_name="geneticka_zprava.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("Vyber alespoň jeden gen.")
