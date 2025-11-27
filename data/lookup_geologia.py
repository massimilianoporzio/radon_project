import csv
import sys

# === CONFIGURAZIONE ===
# Assicurati che questo sia il nome del file CSV che hai estratto da pgAdmin
CSV_FILENAME = "data\\data-1764149181201.csv"
# Il nome della colonna che contiene la descrizione litologica
DESC_COLUMN_NAME = "descript"


def classify_rock_risk(description):
    """
    Classifica il rischio Radon in base alle parole chiave presenti nella descrizione litologica.
    """
    desc_lower = description.lower()

    # --- MOLTO ALTO / ALTO RISCHIO (PRODUZIONE PRIMARIA) ---
    if any(keyword in desc_lower for keyword in ["graniti", "granito", "gneiss", "scisti", "cristalline", "filladi", "quarziti"]):
        return "Alto", "Roccia Madre: Materiale metamorfico o granitico, forte produzione di Uranio/Radio."

    # --- MEDIO RISCHIO (PERMEABILITÀ ALTA / RISALITA FACILE) ---
    if any(
        keyword in desc_lower
        for keyword in ["ghiaie", "sabbie", "conglomerati", "moreniche", "alluvionali", "arenarie", "fratture"]
    ):
        return "Medio", "Permeabilità: Alta. Materiale grossolano che facilita la risalita del gas."

    # --- BASSO RISCHIO (BLOCCO / IMPERMEABILITÀ) ---
    if any(keyword in desc_lower for keyword in ["argille", "marne", "limi", "siltiti", "impermeabili", "calcarei"]):
        return "Basso", "Permeabilità: Bassa. Materiale a grana fine che blocca la risalita del gas."

    # Default
    return "Medio/Sconosciuto", "Classificazione incerta. Necessaria verifica manuale."


def generate_sql_insert(data):
    """
    Genera il comando SQL INSERT da una lista di tuple (descrizione, rischio, motivo).
    """
    sql_header = f"""
-- FILE GENERATO AUTOMATICAMENTE DA mappa_geologia.py
-- Data: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
-- Contiene {len(data)} valori unici estratti dal DB.

-- ATTENZIONE: La mappatura 'Medio/Sconosciuto' NECESSITA DI VERIFICA MANUALE.

CREATE TABLE public.geologia_lookup (
    desc_unit_text VARCHAR(255) PRIMARY KEY,
    livello_rischio_radon VARCHAR(50) NOT NULL,
    motivo VARCHAR(255)
);

INSERT INTO public.geologia_lookup (desc_unit_text, livello_rischio_radon, motivo) VALUES
"""

    sql_values = []
    for description, risk, reason in data:
        # Pulisce la descrizione per l'uso in SQL (escape di apici singoli)
        clean_desc = description.replace("'", "''")
        clean_reason = reason.replace("'", "''")

        sql_values.append(f"('{clean_desc}', '{risk}', '{clean_reason}')")

    return sql_header + ",\n".join(sql_values) + ";\n"


def main():
    try:
        with open(CSV_FILENAME, "r", newline="", encoding="utf-8") as csvfile:
            # Usa DictReader per leggere il CSV con il nome della colonna
            reader = csv.DictReader(csvfile)

            # Estrarre tutti i valori unici dalla colonna specificata
            unique_descriptions = set()
            for row in reader:
                if DESC_COLUMN_NAME in row and row[DESC_COLUMN_NAME].strip():
                    unique_descriptions.add(row[DESC_COLUMN_NAME].strip())

            if not unique_descriptions:
                print("ERRORE: Nessun valore univoco trovato nella colonna 'descript'.")
                return

            mapped_data = []
            for description in sorted(list(unique_descriptions)):
                risk, reason = classify_rock_risk(description)
                mapped_data.append((description, risk, reason))

            # Genera il file SQL
            sql_output = generate_sql_insert(mapped_data)

            # Stampa l'output direttamente nel file che l'utente può copiare
            print("--- INIZIO OUTPUT SQL ---")
            print(sql_output)
            print("--- FINE OUTPUT SQL ---")

    except FileNotFoundError:
        print(f"ERRORE: File '{CSV_FILENAME}' non trovato. Assicurati che sia nella stessa cartella e che il nome sia corretto.")
        sys.exit(1)


if __name__ == "__main__":
    main()
