import streamlit as st
from docx import Document
import pandas as pd
import io

# --- 1. Genetická data s interpretací ---
geneticka_data = {
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

st.title("🧬 Generátor genetické zprávy se šablonou")
st.markdown("Vyber geny a genotypy, vygeneruj zprávu, vlož tabulku do šablony Word.")

# --- 2. Výběr genů a genotypů (radiobuttons) ---
vybrane_geny = {}
st.subheader("Výběr genotypů")

for gen, moznosti in geneticka_data.items():
    with st.expander(f"🧪 {gen}"):
        genotyp = st.radio(
            label=f"Vyber genotyp pro {gen}:",
            options=list(moznosti.keys()),
            key=gen
        )
        vybrane_geny[gen] = genotyp

# --- 3. Vygeneruj DataFrame ---
if vybrane_geny:
    tabulka = []
    for gen, genotyp in vybrane_geny.items():
        info = geneticka_data[gen][genotyp]
        tabulka.append({
            "Gen": gen,
            "Genotyp": genotyp,
            "Klíč": info["KLÍČ"],
            "Interpretace": info["INTERPRETACE"]
        })
    df = pd.DataFrame(tabulka)

    st.subheader("📋 Náhled výsledkové tabulky")
    st.dataframe(df)

    # --- 4. Načtení šablony z rootu projektu (např. GitHub main) ---
    template_path = "Vysledkova_zprava.docx"
    try:
        doc = Document(template_path)
    except Exception as e:
        st.error(f"❌ Nepodařilo se načíst šablonu z '{template_path}': {e}")
        st.stop()

    # --- 5. Najdi místo pro vložení tabulky ---
    target_text = "Datum a čas odběru:"
    insert_index = None
    for i, paragraph in enumerate(doc.paragraphs):
        if target_text in paragraph.text:
            insert_index = i + 2
            break

    if insert_index is not None:
        # --- 6. Vlož tabulku ---
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col

        for _, row in df.iterrows():
            cells = table.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = str(val)

        # Přesun tabulky
        tbl = table._element
        body = doc._body._element
        body.remove(tbl)
        doc.paragraphs[insert_index]._element.addnext(tbl)

        # --- 7. Ulož a nabídni ke stažení ---
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        st.download_button(
            label="📄 Stáhnout hotovou zprávu",
            data=output,
            file_name="Geneticka_zprava.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("❌ Nepodařilo se najít cílové místo pro vložení tabulky.")
else:
    st.info("✅ Vyber alespoň jeden gen pro generování zprávy.")


