import streamlit as st
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
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

# --- 2. Funkce: Vložení tabulky za záložku ---
def vloz_tabulku_za_bookmark(doc, vybrane, bookmark_name="TABULKA"):
    for p in doc.paragraphs:
        for bookmark in p._element.findall(".//w:bookmarkStart", namespaces=p._element.nsmap):
            if bookmark.get(qn("w:name")) == bookmark_name:
                parent = bookmark.getparent()
                idx = list(parent).index(bookmark)

                # Vytvořit tabulku
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

                parent.insert(idx + 1, table._element)
                return True
    return False

# --- 3. UI logika ve Streamlitu ---
st.set_page_config(page_title="Genetická zpráva", page_icon="🧬", layout="centered")
st.title("🧬 Generátor genetické zprávy")

vybrane = {}
for gen in data:
    if st.checkbox(gen, value=False):
        varianty = st.multiselect(f"Varianty pro {gen}:", list(data[gen].keys()), key=gen)
        if varianty:
            vybrane[gen] = varianty

if st.button("📄 Generovat zprávu"):
    if not vybrane:
        st.warning("❗ Vyber alespoň jeden gen a jeho variantu.")
    else:
        try:
            doc = Document("Vysledkova_zprava.docx")
        except Exception as e:
            st.error(f"⚠️ Nepodařilo se načíst šablonu: {e}")
        else:
            success = vloz_tabulku_za_bookmark(doc, vybrane)
            if not success:
                st.error("⚠️ Záložka 'TABULKA' nebyla nalezena v šabloně Word.")
            else:
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.success("✅ Zpráva byla úspěšně vytvořena.")
                st.download_button(
                    label="⬇️ Stáhnout výsledkovou zprávu",
                    data=buffer,
                    file_name="geneticka_zprava.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )


