import streamlit as st
from docx import Document
import pandas as pd
import io

# === 1. Načti vstupní data z Varianty.xlsx ===
@st.cache_data
def nacti_data():
    df = pd.read_excel("Varianty.xlsx")
    df["GEN"] = df["GEN"].ffill()
    varianty_data = []
    for _, row in df.iterrows():
        varianty_data.append({
            "Gen": row["GEN"],
            "Genotyp": row["GENOPYP/VARIANTA"],
            "Zkrácená": row["ZKRÁCENÁ INTERPRETACE"],
            "Interpretace": row.get("INTERPRETACE", ""),
            "Doporuceni": row.get("DOPORUČENÍ", "")
        })
    return pd.DataFrame(varianty_data)

df_all = nacti_data()

# === 2. Uživatelské rozhraní ===
st.title("🧬 Generátor genetické zprávy")
st.markdown("Vyber geny a jejich varianty. Na základě toho se vygeneruje tabulka do Wordu.")

vybrane = {}
for gen in df_all["Gen"].unique():
    moznosti = df_all[df_all["Gen"] == gen]["Genotyp"].tolist()
    with st.expander(f"🧬 {gen}"):
        vyber = st.multiselect(f"Zvol genotyp(y) pro {gen}:", moznosti, key=gen)
        if vyber:
            vybrane[gen] = vyber

# === 3. Generování výsledků ===
if vybrane:
    rows = []
    for gen, genotypy in vybrane.items():
        for g in genotypy:
            zaznam = df_all[(df_all["Gen"] == gen) & (df_all["Genotyp"] == g)].iloc[0]
            rows.append({
                "Gen": zaznam["Gen"],
                "Genotyp": zaznam["Genotyp"],
                "Zkrácená": zaznam["Zkrácená"],
                "Doporučení": zaznam["Doporuceni"]
            })
    df_final = pd.DataFrame(rows)

    # === 4. Načti Word šablonu ===
    try:
        doc = Document("Vysledkova_zprava.docx")
    except Exception as e:
        st.error(f"❌ Nepodařilo se načíst šablonu: {e}")
        st.stop()

    # === 5. Najdi a nahraď text 'TABULKA' tabulkou ===
    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if "TABULKA" in para.text:
            insert_index = i
            doc.paragraphs[i].text = ""  # vymažeme placeholder
            break

    if insert_index is None:
        st.error("❌ Text 'TABULKA' nebyl nalezen v šabloně.")
        st.stop()

    # === 6. Vlož tabulku ===
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    headers = ["Gen", "Genotyp", "Zkrácená", "Doporučení"]
    for i, col in enumerate(headers):
        table.rows[0].cells[i].text = col

    for _, row in df_final.iterrows():
        cells = table.add_row().cells
        cells[0].text = row["Gen"]
        cells[1].text = row["Genotyp"]
        cells[2].text = row["Zkrácená"]
        cells[3].text = row["Doporučení"]

    # Vlož tabulku do dokumentu
    tbl = table._element
    doc.paragraphs[insert_index]._element.addnext(tbl)

    # === 7. Ulož a nabídni ke stažení ===
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
    st.info("✅ Vyber alespoň jeden genotyp pro generování zprávy.")
