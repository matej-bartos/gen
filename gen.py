import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pandas as pd
import io
import requests

st.title("🧬 Generátor genetické zprávy")

# --- Načtení XLSX z GitHubu ---
url = "https://github.com/matej-bartos/gen/raw/main/Varianty.xlsx"
try:
    response = requests.get(url)
    response.raise_for_status()
    df_all = pd.read_excel(io.BytesIO(response.content), sheet_name="List1")
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
    for gen in sorted(set(df_sekce["Gen"])):
        moznosti = df_sekce[df_sekce["Gen"] == gen]["Genotyp"].dropna().astype(str).unique().tolist()
        if moznosti:
            zvolene = st.multiselect(f"{gen}", moznosti, key=gen)
            if zvolene:
                vybrane[gen] = zvolene

# --- Pomocné funkce ---
def merge_gen_cells(table):
    current_gen = None
    for i in range(1, len(table.rows)):
        cell = table.cell(i, 0)
        gen_value = cell.text.strip()
        if gen_value == current_gen:
            cell.text = ""
        else:
            current_gen = gen_value

def set_cell_background(cell, color_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

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

    # --- Tabulka ---
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

    for sekce in df_final["Sekce"].unique():
        df_sekce = df_final[df_final["Sekce"] == sekce]

        row = table.add_row()
        merged = row.cells[0].merge(row.cells[1]).merge(row.cells[2])
        merged.text = sekce
        set_cell_background(merged, "00FFFF")
        para = merged.paragraphs[0]
        run = para.runs[0]
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 32, 96)
        para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # ✅ zarovnání na střed

        gen_last = None
        for _, row_data in df_sekce.iterrows():
            row_cells = table.add_row().cells
            row_cells[0].text = str(row_data["Gen"]) if row_data["Gen"] != gen_last else ""
            gen_last = row_data["Gen"]

            row_cells[1].text = str(row_data["Genotyp"])
            row_cells[2].text = str(row_data["Interpretace"])

            for i in [0, 1]:
                for run in row_cells[i].paragraphs[0].runs:
                    run.font.size = Pt(10)

            for run in row_cells[2].paragraphs[0].runs:
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

