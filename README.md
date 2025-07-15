# 🧬 Generátor genetické zprávy

Interaktivní aplikace postavená na [Streamlit](https://streamlit.io/) pro výběr genetických variant a automatické generování personalizované zprávy ve formátu **.docx**.

---

## 🔍 Hlavní funkce

- Načtení excelového souboru **Varianty.xlsx** přímo z GitHubu  
- Interaktivní výběr genotypů podle sekcí a genů  
- Automatické sestavení a vložení tabulky do Word šablony **Vysledkova_zprava.docx**  
- Barevné oddělení sekcí a inteligentní sloučení buněk pro geny s více variantami  
- Stáhnutí výsledné zprávy jedním kliknutím

---

## 📂 Struktura repozitáře

📦 gen/
├── app.py # Hlavní Streamlit skript
├── Varianty.xlsx # Zdroj dat s genotypy a interpretacemi
├── Vysledkova_zprava.docx # Word šablona (obsahuje text 'TABULKA')
└── README.md # Tento soubor


---
📄 Vstupní data – Varianty.xlsx

| Sloupec          | Popis                               |
| ---------------- | ----------------------------------- |
| **Sekce**        | Tematický blok (např. Metabolismus) |
| **Gen**          | Název genu                          |
| **Genotyp**      | Varianta (např. CC, \*2/\*2…)       |
| **Interpretace** | Vysvětlení vlivu varianty           |


🧾 Šablona zprávy – Vysledkova_zprava.docx
Musí obsahovat textový marker TABULKA – na jeho místo se vloží vygenerovaná tabulka.

Styl tabulky: Table Grid (lze změnit v kódu).

📝 Editace kódu
Hlavní bloky skriptu app.py jsou odděleny komentáři # === Název sekce ===.

Kódová sekce	Účel
Načtení Excelu	Stáhne Varianty.xlsx z GitHubu a validuje povinné sloupce.
Výběr genotypů	Vytváří uživatelské rozhraní pro výběr variant pomocí st.multiselect.
Generování zprávy	Načte Word šablonu, sestaví tabulku, formátuje sekce, sloučí buňky pro geny s více variantami
Stáhnutí výstupu	Nabídne hotový dokument ke stažení přes st.download_button.

Pomocná funkce set_cell_background nastavuje barvu pozadí buněk přímo přes XML (python-docx).
