import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
import pandas as pd
import io
import requests

st.title("🧬 Generátor genetické zprávy")
st.markdown("Načti genetická data z GitHubu a vytvoř personalizovanou zprávu ve formátu Word.")

# --- Načtení XLSX z GitHubu ---
url = "https://github.com/matej-bartos/gen/raw/main/Varianty.xlsx"  # ⚠️ RAW odkaz
try:
    response = requests.get(url)
    response.raise_for_status()
    xls_data = pd.read_excel(io.BytesIO(response.content), sheet_name="List1")
except Exception as e:
    st.error(f"❌ Chyba při načítání Excelu z GitHubu: {e}")
    st.stop()

# --- Úprava sloupců ---
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
    moznosti = df_all[df_all["Gen"] == gen]["Genotyp"].dropna().astype(str).unique().tolist()
    if moznosti:
        with st.expander(f"🧪 {gen}"):
            zvolene = st.multiselect(f"Zvol genotyp(y) pro {gen}:", moznosti, key=gen)
            if zvolene:
                vybrane[gen] = zvolene

# --- Funkce pro sloučení shodných buněk ve sloupci GEN ---
def merge_gen_cells(table):
    current_gen = None
    merge_start = None
    for i in range(1, len(table.rows)):
        cell = table.cell(i, 0)
        gen_value = cell.text.strip()
        if gen_value == current_gen:
            continue
        else:
            if merge_start is not None and i - merge_start > 1:
                cell_to_merge = table.cell(merge_start, 0)
                for j in range(merge_start + 1, i):
                    cell_to_merge.merge(table.cell(j, 0))
                for para in cell_to_merge.paragraphs:
                    para.alignment = 1  # center
            current_gen = gen_value
            merge_start = i
    if merge_start is not None and len(table.rows) - merge_start > 1:
        cell_to_merge = table.cell(merge_start, 0)
        for j in range(merge_start + 1, len(table.rows)):
            cell_to_merge.merge(table.cell(j, 0))
        for para in cell_to_merge.paragraphs:
            para.alignment = 1  # center

# --- Vygeneruj zprávu ---
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

    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if "TABULKA" in para.text:
            insert_index = i
            doc.paragraphs[i].text = ""
            break

    if insert_index is None:
        st.error("❌ Text 'TABULKA' nebyl nalezen v šabloně.")
        st.stop()

    # --- Vlož tabulku ---
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.autofit = True

    headers = ["GEN", "VÝSLEDNÁ VARIANTA", "INTERPRETACE"]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.size = Pt(9)

    for _, row in df_final.iterrows():
        cells = table.add_row().cells
        cells[0].text = st
