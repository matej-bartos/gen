import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
import pandas as pd
import io
import requests

st.title("🧬 Generátor genetické zprávy")
st.markdown("Soubor `Varianty.xlsx` se načítá automaticky z GitHubu (list `Sheet1`).")

# --- Načtení XLSX z GitHubu ---
url = "https://github.com/matej-bartos/gen/raw/main/Varianty.xlsx"  # ✅ uprav podle své repo struktury
try:
    response = requests.get(url)
    response.raise_for_status()
    df_all = pd.read_excel(io.BytesIO(response.content), sheet_name="Sheet1")
except Exception as e:
    st.error(f"❌ Chyba při načítání Excelu z GitHubu: {e}")
    st.stop()

# --- Validace sloupců ---
required_cols = ["Sekce", "Gen", "Genotyp", "Interpretace"]
if list(df_all.columns[:4]) != required_cols:
    st.error(f"❌ Soubor musí obsahovat sloupce: {', '.join(required_cols)}")
    st.stop()

df_all = df_all.dropna(subset=required_cols)

# --- Výběr genů podle sekcí ---
vybrane = {}
for sekce in df_all["Sekce"].unique():
    st.subheader(sekce)
    df_sekce = df_all[df_all["Sekce"] == sekce]
    for gen in df_sekce["Gen"].unique():
        moznosti = df_sekce[df_sekce["Gen"] == gen]["Genotyp"].dropna().astype(str).unique().tolist()
        if moznosti:
            zvolene = st.multiselect(f"{gen}", moznosti, key=gen)
            if zvolene:
                vybrane[gen] = zvolene

# --- Sloučení stejných buněk GEN ---
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
                    para.alignment = 1
            current_gen = gen_value
            merge_start = i
    if merge_start is not None and len(table.rows) - merge_start > 1:
        cell_to_merge = table.cell(merge_start, 0)
        for j in range(merge_start + 1, len(table.rows)):
            cell_to_merge.merge(table.cell(j, 0))
        for para in cell_to_merge.paragraphs:
            para.alignment = 1

# --- Generování zprávy ---
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

    # --- Vytvoření tabulky ---
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.autofit = True

    headers = ["GEN", "VÝSLEDNÁ VARIANTA", "INTERPRETACE"]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.size = Pt(10)

    for _, row in df_final.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row["Gen"])
        cells[1].text = str(row["Genotyp"])
        cells[2].text = str(row["Interpretace"])

        for i in [0, 1]:
            for run in cells[i].paragraphs[0].runs:
                run.font.size = Pt(10)
        for run in cells[2].paragraphs[0].runs:
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 32, 96)

    merge_gen_cells(table)

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
