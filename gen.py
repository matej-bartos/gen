import streamlit as st
from docx import Document

# Ukázková data
data = [
    {
        "GEN": "MCM6 13910",
        "VARIANTA": "TT",
        "KLÍČ": "+/+",
        "INTERPRETACE": "Vrozená tolerance laktózy. Laktáza se ve střevě tvoří celoživotně. Není potřeba dodržovat bezlaktózovou dietu."
    },
    {
        "GEN": "DAO",
        "VARIANTA": "CT",
        "KLÍČ": "+/-",
        "INTERPRETACE": "Riziko histaminové intolerance spojené s migrénami. Doporučena nízkohistaminová dieta."
    },
    {
        "GEN": "PEMT (rs7946)",
        "VARIANTA": "CT",
        "KLÍČ": "+/-",
        "INTERPRETACE": "Pomalejší odbourávání tuků v játrech. Riziko dysfunkce při nedostatku cholinu."
    }
]

st.title("Genetický výstup – generátor zpráv")

gen_input = st.text_input("Zadej název genu (více genů odděl čárkou, např. DAO, MCM6 13910):")

if st.button("Generovat zprávu"):
    geny = [g.strip().lower() for g in gen_input.split(",")]
    nalezene_zaznamy = [z for z in data if z["GEN"].lower() in geny]

    if nalezene_zaznamy:
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        
        # Vytvoříme tabulku - počet řádků = počet genů + 1 (pro hlavičku)
        table = doc.add_table(rows=len(nalezene_zaznamy) + 1, cols=4)
        table.style = 'Light List Accent 1'
        
        # Hlavička tabulky
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "GEN"
        hdr_cells[1].text = "VARIANTA"
        hdr_cells[2].text = "KLÍČ"
        hdr_cells[3].text = "INTERPRETACE"
        
        # Vyplnění dat
        for i, zaznam in enumerate(nalezene_zaznamy, start=1):
            row_cells = table.rows[i].cells
            row_cells[0].text = zaznam["GEN"]
            row_cells[1].text = zaznam["VARIANTA"]
            row_cells[2].text = zaznam["KLÍČ"]
            row_cells[3].text = zaznam["INTERPRETACE"]
        
        filename = "geneticky_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Žádný gen zadaný v seznamu nebyl nalezen v databázi.")

