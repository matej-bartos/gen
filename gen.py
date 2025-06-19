import streamlit as st
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
import io

# Data
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

# Funkce pro vložení tabulky za záložku
def vloz_tabulku_za_bookmark(doc, vybrane, bookmark_name="TABULKA"):
    # Najdi XML element záložky
    for p in doc.paragraphs:
        for bookmark in p._element.findall(".//w:bookmarkStart", namespaces=p._element.nsmap):
            if bookmark.get(qn("w:name")) == bookmark_name:
                parent = bookmark.getparent()
                idx = list(parent).index(bookmark)

                # Vytvoř tabulku
                table = doc.add_table(rows=1, cols=4)
                table.style = "Table Grid"
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

                # Vlož tabulku za záložku
                parent.insert(idx + 1, table._element)
                return True
    return False

# Streamlit UI
st.title("🧬 Generátor genetické zprávy (se záložkou)")

vybrane = {}
for gen in data:
    if st.checkbox(gen):
        varianty = st.multiselect(f"Varianty pro {gen}:", list(data[gen].keys()), key=gen)
        if varianty:
            vybrane[gen] = varianty

if st.button("📄 Generovat zprávu"):
    if vybrane:
        doc = Document("Vysledkova_zprava_s_bookmarkem.docx")
        success = vloz_tabulku_za_bookmark(doc, vybrane)

        if not success:
            st.error("Záložka 'TABULKA' nebyla nalezena v dokumentu.")
        else:
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
