import streamlit as st
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
import io

# Slovník genetických dat
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

# Funkce pro vložení tabulky místo placeholderu
def vloz_tabulku_na_misto(doc, vybrane):
    for paragraph in doc.paragraphs:
        if '###TABULKA###' in paragraph.text:
            # Odstranit placeholder odstavec
            p = paragraph._element
            p.getparent().remove(p)

            # Vložit tabulku
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.LEFT

            hdr = table.rows[0].cells
            hdr[0].text = "GEN"
            hdr[1].text = "VÝSLEDNÁ VARIANTA"
            hdr[2].text = "Dle klíče"
            hdr[3].text = "INTERPRETACE"

            for gen, varianty in vybrane.items():
                for var in varianty:
                    row = table.add_row().cells
                    row[0].text = gen
                    row[1].text = var
                    row[2].text = data[gen][var]["KLÍČ"]
                    row[3].text = data[gen][var]["INTERPRETACE"]
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
            doc = Document("Výsledková zpráva.docx")  # Soubor musí být ve stejné složce jako app.py
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



