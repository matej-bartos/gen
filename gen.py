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

gen_input = st.text_input("Zadej název genu (např. DAO):")

if st.button("Generovat zprávu"):
    zaznam = next((z for z in data if z["GEN"].lower() == gen_input.lower()), None)
    if zaznam:
        # Vytvoření Word dokumentu
        doc = Document()
        doc.add_heading("Výsledek genetického testu", level=1)
        
        # Vytvoření tabulky s 4 řádky a 2 sloupci
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Light List Accent 1'  # Lze změnit styl tabulky
        
        # Hlavičky
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Kategorie"
        hdr_cells[1].text = "Hodnota"
        
        # Data
        row_cells = table.rows[1].cells
        row_cells[0].text = "GEN"
        row_cells[1].text = zaznam["GEN"]
        
        row_cells = table.rows[2].cells
        row_cells[0].text = "VARIANTA"
        row_cells[1].text = zaznam["VARIANTA"]
        
        row_cells = table.rows[3].cells
        row_cells[0].text = "KLÍČ"
        row_cells[1].text = zaznam["KLÍČ"]
        
        # Přidat další odstavec s interpretací pod tabulku
        doc.add_paragraph("\nINTERPRETACE:")
        doc.add_paragraph(zaznam["INTERPRETACE"])
        
        filename = f"{zaznam['GEN'].replace(' ', '_')}_vysledek.docx"
        doc.save(filename)

        with open(filename, "rb") as file:
            st.download_button("📄 Stáhnout zprávu ve Wordu", file, file_name=filename)
    else:
        st.warning("Gen nebyl nalezen v databázi.")


