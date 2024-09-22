import json
import os
from prettytable import PrettyTable
"""
ConvertPrompts konvertiert lediglich eine TXT-Datei in eine Ladefähige JSON-Datei.

Die Erstellung der TXT-Dateien ist deutlich einfacher als die Erstellung der entsprechenden JSON-Datei.
"""
class ConvertPromptToJSON:
    def __init__(self, file_path):
        """
        Initialisiert die Klasse mit dem Pfad zur Eingabedatei.

        :param file_path: Pfad zur Textdatei, die geladen und konvertiert werden soll.
        """
        self.file_path = file_path
        self.data = []

    def load_and_convert(self, raw_data:list=[], file_name:str=None, save_to_file:bool=True):
        """
        Lädt die Datei file_name oder import Informationen aus raw_data.
        Die Datei hat folgenden aufbau

        [
            {'prompt':<value>, 'template':<value>, 'code':<value>}, ...
        ]

         """
        try:
            #
            # entweder liegen die Daten schon als raw_data vor oder sie werden aus file_name gelesen
            lines=[]
            if file_name is not None:
                #
                # es wurde explizit ein file_name angeben
                file_name = os.path.join(self.file_path, file_name)
                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                except FileExistsError as err:
                    raise FileExistsError(f"Prompt-File '{file_name} nicht vorhanden")
            elif len(raw_data) > 0:
                #
                # es wurden mehrere prompt-dateien im Verzeichnis gefunden und geladen
                lines = raw_data
            else:
                raise ValueError("raw_data leer  und kein File_Name ")
            

            current_block = {}
            current_section = None
            counts = {'prompt':0, 'template':0, 'code':0}
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                # Prüfen auf case-insensitive Schlüsselwörter
                if line.startswith('#'):            #=Kommentarzeile, wird ignoriert
                    continue
                if line.upper().startswith("PROMPT:"):
                    current_section = "prompt"
                    counts[current_section] = counts[current_section] + 1
                    current_block[current_section] = line[len("PROMPT:"):].strip()
                elif line.upper().startswith("TEMPLATE:"):
                    current_section = "template"
                    current_block[current_section] = line[len("TEMPLATE:"):].strip()
                    # nur zählen, wenn auch Text vorhanden ist
                    if (len(current_block[current_section])> 0):
                        counts[current_section] = counts[current_section] + 1
                elif line.upper().startswith("CODE:"):
                    current_section = "code"
                    current_block[current_section] = line[len("CODE:"):]
                    # nur zählen, wenn auch Text vorhanden ist
                    if (len(current_block[current_section])> 0):
                        counts[current_section] = counts[current_section] + 1
                elif line == "|":  # Abschluss eines Blocks
                    if current_block:
                        self.data.append(current_block)
                        current_block = {}
                        current_section = None
                else:
                    # Zeile zum aktuellen Abschnitt hinzufügen
                    if current_section in current_block:
                        current_block[current_section] += " " + line
                    else:
                        current_block[current_section] = line

            # Letzten Block hinzufügen, falls die Datei nicht mit einem Pipe-Zeichen endet
            if current_block:
                self.data.append(current_block)

            if save_to_file:
                out_file = self.save_as_json()
            else:
                out_file = "no saving to json"

            error = None
            if counts['prompt'] != (counts['template'] + counts['code']):
                error = "Anzahl PROMPTS <> (TEMPLATES + CODE) - Fehlerhafte Prompt-Datei."
                self.data = []
            tbl = PrettyTable(['PROMPTS', 'TEMPLATE','CODE','PROMPT-FILE','OUTPUT-FILE', 'ERROR'])
            tbl.add_row([counts['prompt'], counts['template'], counts['code'], file_name, out_file, error ])
            print(tbl)
            return self.data

        except Exception as e:
            print(f"Fehler beim Verarbeiten der Datei: {e}")

    def save_as_json(self):
        """
        Speichert die konvertierten Daten als JSON-Datei.
        """
        try:
            json_file_path = self.file_path.rsplit('.', 1)[0] + '.json'
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4, ensure_ascii=False)
            #print(f"--------------------- ENDE ---------------------\nJSON-Datei erfolgreich gespeichert unter: {json_file_path}")
            return json_file_path
        except Exception as e:
            print(f"Fehler beim Speichern der JSON-Datei: {e}")

# Beispielnutzung:
#converter = ConvertPromptToJSON('genai_training/prompts/prompts_shorts.txt')
#converter.load_and_convert()
