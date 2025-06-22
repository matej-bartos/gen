import streamlit as st
from docx import Document
import pandas as pd
import io

# === Vstupní genetická data přímo ve skriptu ===
varianty_data = [
    {"Gen": "MCM6 13910", "Genotyp": "TT", "Klíč": "+/+", "Interpretace": "Vrozená tolerance laktózy."},
    {"Gen": "MCM6 13910", "Genotyp": "CT", "Klíč": "+/-", "Interpretace": "Částečná tolerance laktózy."},
    {"Gen": "MCM6 13910", "Genotyp": "CC", "Klíč": "-/-", "Interpretace": "Nedostatek laktázy."},
    {"Gen": "DAO", "Genotyp": "CC", "Klíč": "+/+", "Interpretace": "Normální aktivita DAO."},
    {"Gen": "DAO", "Genotyp": "CT", "Klíč": "+/-", "Interpretace": "Riziko histaminové intolerance."},
    {"Gen": "DAO", "Genotyp": "TT", "Klíč": "-/-", "Interpretace": "Nízká aktivita DAO."},
    {"Gen": "PEMT (rs7946)", "Genotyp": "CC", "Klíč": "+/+", "Interpretace": "Normální metabolismus tuků."},
    {"Gen": "PEMT (rs7946)", "Genotyp": "CT", "Klíč": "+/-", "Interpretace": "Pomalejší odbourávání tuků."},
    {"Gen": "PEMT (rs7946)", "Genotyp": "TT", "Klíč": "-/-", "Interpretace": "Výrazně snížený metabolismus tuků."},
    {"Gen": "COMT", "Genotyp": "Val/Val", "Klíč": "+/+", "Interpretace": "Rychlé odbourávání - horší soustředění."},
    {"Gen": "COMT", "Genotyp": "Val/Met", "Klíč": "+/-", "Interpretace": "Vyvážené odbourávání dopaminu."},
    {"Gen": "COMT", "Genotyp": "Met/Met", "Klíč": "-/-", "Interpretace": "Pomalé odbourávání - vyšší stresová citlivost."},
    {"Gen": "MAO-A", "Genotyp": "TT", "Klíč": "+/+", "Interpretace": "Vysoká aktivita - sklon k úzkostem."},
    {"Gen": "MAO-A", "Genotyp": "TC", "Klíč": "+/-", "Interpretace": "Střední aktivita MAO-A."},
    {"Gen": "MAO-A", "Genotyp": "CC", "Klíč": "-/-", "Interpretace": "Nižší aktivita - odolnější vůči stresu."},
    {"Gen": "ACTN3", "Genotyp": "CC", "Klíč": "+/+", "Interpretace": "Svaly pro výbušnost a sprint."},
    {"Gen": "ACTN3", "Genotyp": "CT", "Klíč": "+/-", "Interpretace": "Univerzální typ svalů."},
    {"Gen": "ACTN3", "Genotyp": "TT", "Klíč": "-/-", "Interpretace": "Svaly pro vytrvalost."},
    {"Gen": "ACE I/D", "Genotyp": "I/I", "Klíč": "+/+", "Interpretace": "Vytrvalostní typ."},
    {"Gen": "ACE I/D", "Genotyp": "I/D", "Klíč": "+/-", "Interpretace": "Smíšený typ."},
    {"Gen": "ACE I/D", "Genotyp": "D/D", "Klíč": "-/-", "Interpretace": "Silový typ."},
    {"Gen": "ApoE", "Genotyp": "E2/E3", "Klíč": "+/+", "Interpretace": "Nízké riziko Alzheimerovy choroby."},
    {"Gen": "ApoE", "Genotyp": "E3/E4", "Klíč": "+/-", "Interpretace": "Mírně zvýšené riziko Alzheimerovy choroby."},
    {"Gen": "ApoE", "Genotyp": "E4/E4", "Klíč": "-/-", "Interpretace": "Vyšší riziko Alzheimerovy choroby."},
    {"Gen": "MTHFR", "Genotyp": "CC", "Klíč": "+/+", "Interpretace": "Efektivní metabolismus folátu."},
    {"Gen": "MTHFR", "Genotyp": "CT", "Klíč": "+/-", "Interpretace": "Snížená přeměna folátu."},
    {"Gen": "MTHFR", "Genotyp": "TT", "Klíč": "-/-", "Interpretace": "Výrazně snížená přeměna folátu – riziko vysokého homocysteinu."}
]

# --- UI ---
st.title("🧬 Generátor genetické zprávy")
st.markdown("Vyber geny a jeden nebo více genotypů, a stáhni finální zprávu jako Word dokument.")

# --- Seskupení podle genů ---
df_all = pd.DataFrame(varianty_data)
vybrane = {}

for gen in df_all["Gen"].unique():
    moznosti = df_all[df_all["Gen"] == gen]["Genotyp"].tolist()
    with st.expander(f"🧪 {gen}"):
        zvolene = st.multiselect(f"Zvol genotyp(y) pro {gen}:", moznosti, key=gen)
        if zvolene:
            vybrane[gen] = zvolene

# --- Zpracuj výběr ---
if vybrane:
    vysledky = []
    for gen, seznam in vybrane.items():
        for g in seznam:
            z = df_all[(df_all["Gen"] == gen) & (df_all["Genotyp"] == g)].iloc[0]
            vysledky.append({
                "Gen": z["Gen"],
                "Genotyp": z["Genotyp"],
                "Klíč": z["Klíč"],
                "Interpretace": z["Interpretace"]
            })
    df_final = pd.DataFrame(vysledky)

    # --- Načti šablonu ---
    try:
        doc = Document("Vysledkova_zprava.docx")
    except Exception as e:
        st.error(f"❌ Nepodařilo se načíst šablonu: {e}")
        st.stop()

    # --- Najdi místo 'TABULKA' ---
    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if "TABULKA" in para.text:
            insert_index = i
            doc.paragraphs[i].text = ""
            break

    if insert_index is None:
        st.error("❌ Text 'TABULKA' nebyl nalezen v dokumentu.")
        st.stop()

    # --- Vlož tabulku ---
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    for i, col in enumerate(["Gen", "Genotyp", "Klíč", "Interpretace"]):
        table.rows[0].cells[i].text = col

    for _, row in df_final.iterrows():
        cells = table.add_row().cells
        cells[0].text = row["Gen"]
        cells[1].text = row["Genotyp"]
        cells[2].text = row["Klíč"]
        cells[3].text = row["Interpretace"]

    tbl = table._element
    doc.paragraphs[insert_index]._element.addnext(tbl)

    # --- Ulož a nabídni ke stažení ---
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
