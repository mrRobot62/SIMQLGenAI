import json
import pandas as pd

class PromptToJsonConverter:
    """ 
    Liest eine NLP-Beschreibungsdatei ein und konvertiert diese in eine Json-Struktur oder DataFrame.
    Der Aufbau der NLP-Beschreibungsdatei kann sich über mehrere Zeilen erstrecken und hat folgenden Aufbau
    PROMPT#Template|

    PROMPT:
    NLP Beschreibungstext inkl. Sonderzeichen, erstreckt sich in der Regel über mehrere Zeilen
    # Trennzeichen zwischen Prompt und Template
    
    Template:
    Verweis auf das zu verwendende DSL-Template, Darf nur aus einem Wort bestehen
    Dieses Wort entspricht dem Base-File-Name des Templates


    """
    def __init__(self, file_path):
        self.file_path = file_path      # beinhaltet Pfad & Dateiname
        self.data = []

    def import_text_file(self):
        """Liest die Textdatei ein und parst die Daten basierend auf der speziellen Struktur."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            record = {'text': '', 'template': ''}
            for line in lines:
                line = line.strip()
                if line == '|':  # Datenzeile endet
                    if record['text'] and record['template']:
                        self.data.append(record)
                    record = {'text': '', 'template': ''}
                elif '#' in line:  # Trennung zwischen Beschreibungstext und Template
                    parts = line.split('#', 1)
                    record['text'] += parts[0].strip()
                    record['template'] = parts[1].strip()
                else:
                    record['text'] += line.strip() + ' '  # Fortsetzen der Beschreibung

            # Letztes Element hinzufügen, falls Datei nicht mit '|' endet
            if record['text'] and record['template']:
                self.data.append(record)
        except Exception as e:
            print(f"Fehler beim Importieren der Datei: {e}")

    @property
    def get_json_data(self) -> list:
        """ Rückgabe des konvertierten Prompt-Datenfiles"""
        return self.data
    
    def save_as_json(self):
        """Speichert die geparsten Daten als JSON-Datei."""
        try:
            json_file_path = self.file_path.rsplit('.', 1)[0] + '.json'
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON-Datei gespeichert unter: {json_file_path}")
        except Exception as e:
            print(f"Fehler beim Speichern der JSON-Datei: {e}")

    def get_dataframe(self):
        """Gibt die Daten als Pandas DataFrame zurück."""
        try:
            return pd.DataFrame(self.data)
        except Exception as e:
            print(f"Fehler beim Erstellen des DataFrames: {e}")
            return pd.DataFrame()  # Leeres DataFrame im Fehlerfall zurückgeben



# Beispielnutzung: 
# Unit-Test
# converter = PromptToJsonConverter('genai_training_data/nlp_data/simql_prompts.txt')
# converter.import_text_file()
# converter.save_as_json()
# prompts = converter.get_json_data
# print(f"Prompts: {prompts}")
# df = converter.get_dataframe()
# print(df)
