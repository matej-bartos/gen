import streamlit as st
from docx import Document
import pandas as pd
import io
import requests

st.title("🧬 Generátor genetické zprávy")
st.markdown("Tento nástroj načítá genetická data z GitHubu (soubor XLSX) a umožňuje vygenerovat personalizovanou zprávu.")

# --- Načtení XLSX z GitHubu ---
url = "https://github.com/matej-bartos/gen/raw/main/Varianty.xlsx"  # ⬅️ musí to být raw URL!
try:
    response = requests.get(url)
    response.raise_for_status()
    xls_data = pd.read_excel(io.BytesIO(response.content), sheet_name="List1")
except Exception as e:
    st.error(f"❌ Chyba při načítání Excelu z GitHubu: {e}")
    st.stop()

# --- Úprava názvů sloupců ---
df_all = xls_data.rename(columns={
    "GEN": "Gen",
    "Genotyp": "Genotyp",
    "Intepretace": "Interpretace"
})

# --- Validace sloupců ---
required_cols = {"Gen", "Genotyp", "Interpretace"}
if not required_cols.issubset(df_all.columns):
    st.error(f"❌ XLSX musí obsahovat sloupce: {', '.join(required_cols)}.")
    st.stop()

# --- Výběr genů a genotypů ---
vybrane = {}
for gen in df_all["Gen"].unique():
    moznosti = df_all[df_all["Gen"] == gen]["Genotyp"].tolist()
    with st.expander(f"🧪 {gen}"):
        zvolene = st.multiselect(f"Zvol genotyp(y) pro {gen}:", moznosti, key=gen)
        if zvolene:
            vybrane[gen] = zvolene

# --- Zpracování výběru ---
if vybrane:
    vysledky = []
    for gen, seznam in vybrane.items():
        for g in seznam:
            z = df_all[(df_all["Gen"] == gen) & (df_all["Genotyp"] == g)].iloc[0]
            vysledky.append(z)
    df_final = pd.DataFrame(vysledky)

    try:
        doc = Document("Vysledkova_zprava.docx")
    except Exception as e:
        st.error(f"❌ Nepodařilo se načíst šablonu: {e}")
        st.stop()

    # --- Najdi a nahraď 'TABULKA' ---
    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if "TABULKA" in para.text:
            insert_index = i
            doc.paragraphs[i].text = ""
            break

    if insert_index is None:
        st.error("❌ Text 'TABULKA' nebyl nalezen v šabloně.")
        st.stop()

    # --- Vlož tabulku bez sloupce 'Klíč' ---
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    for i, col in enumerate(["Gen", "Genotyp", "Interpretace"]):
        table.rows[0].cells[i].text = col

    for _, row in df_final.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row["Gen"])
        cells[1].text = str(row["Genotyp"])
        cells[2].text = str(row["Interpretace"])

    tbl = table._element
    doc.paragraphs[insert_index]._element.addnext(tbl)

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
