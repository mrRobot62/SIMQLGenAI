import json
import re
from pathlib import Path
import os

class TextToJsonConverter:
    """
    Diese Klasse liest eine rein SIMQL-Trainsdatei ein und wandelt diese als JSON-Objekt um. Diese JSON-Datei kann für zukünftige Trainsings gespeichert
    werden.

    Das Konvertieren muss dann durchgeführt werden, wenn man neue Trainsingsdaten erstellt hat und diese für zukünftige Trainings genutzt werden soll.

    Aufbau der reinen Trainings-Datendatei:
    Prompt-Text<tab>SIMQL-Code
    Beispiel:
        Berechne Daten mit mp1 und aggregiere die Werte.    var1 = compute data(mp1, math=agg)
        Verwende mp1, um die Daten zu berechnen und nutze eine Aggregationsfunktion.    var1 = compute data(mp1, math=agg)

    JSON-Output:
    [
        {"text":"Berechne Daten mit mp1 und aggregiere die Werte.", "code":"var1 = compute data(mp1, math=agg)"},
        {"text":"Verwende mp1, um die Daten zu berechnen und nutze eine Aggregationsfunktion.", "code":"var1 = compute data(mp1, math=agg)"},
    ]
    """

    def __init__(self, path, input_file, output_file_path=None, sep='[#;\t]', append=False):
        """
        Initialisiert den TextToJsonConverter mit dem Pfad zur Eingabedatei und zur Ausgabedatei.
        
        :param path: Pfad zur Textdatei, die gelesen werden soll. Dieser Pfad ist auch der Default ausgabepfad
        :param input_file: Textdatei, die gelesen werden soll.
        :param output_file_path: Default None: dann wird der Pfad verwendet und der Ausgabename generiert (Name = input_file mit suffix .json)
        :param sep: RegEx für mögliche Separatoren
        :param append: True, dann wird eine bestehende JSON erweitert, Default False=eine bestehende Datei wird überschrieben.
        """
        self.path = path
        self.input_file = os.path.join(path, input_file)
        if output_file_path is None:
            output_file_path = Path(input_file).stem
            output_file_path = os.path.join(self.path,output_file_path) + '.json'
        else:        
            self.output_file_path = output_file_path
        self.separators = sep
        self.append = append

    def read_text_file(self):
        """
        Liest den Inhalt der Textdatei, verarbeitet jede Zeile und gibt eine Liste von Dictionaries zurück.
        
        :return: Liste von Dictionaries mit "text" und "code".
        """
        data = []
        with open(self.input_file_path, 'r') as file:
            for line in file:
                if line == '\n' or len(line) <= 1:
                    continue
                parts = re.split(self.separators, line)
#                parts = line.strip().split('\t')  # Zeile nach Tabulator trennen
                if len(parts) == 2:  # Sicherstellen, dass genau zwei Teile vorhanden sind
                    entry = {"text": parts[0].strip(), "code": parts[1].strip()}
                    data.append(entry)
                elif len(parts) == 1:
                    print(f"Trainingsdatensatz '{line}' enthält keinen verwertbare Code-Informationen. Fehlt eine Tabulator?")
        print(f"{len(data)} Traingsdatensätze geladen")
        return data

    def write_json_file(self, data):
        """
        Schreibt die Daten in eine JSON-Datei.
        
        :param data: Die zu speichernden Daten (Liste von Dictionaries).
        """
        flags = ("a+" if self.append else "w+")

        with open(self.output_file_path, flags) as file:
            json.dump(data, file, indent=4)

    def load_json_file(self, json_file):
        """
        Lädt den Inhalt der JSON-Datei und gibt ihn als Liste von Dictionaries zurück.
        
        :return: Liste von Dictionaries, die in der JSON-Datei gespeichert sind.
        """
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data

    def convert(self):
        """
        Konvertiert den Inhalt der Textdatei in JSON-Format und speichert es.
        """
        data = self.read_text_file()
        self.write_json_file(data)

    @property
    def out_path_file(self):
        """Output-File-Name mit Pfad"""
        return self.output_file_path
    @property
    def out_file(self):
        """Output-File-Name ohne Pfad"""
        return os.path.basename(self.output_file_path)
    

# Nutzung der Klasse
train_path = "genai_training_data"
train_txt_file = "train_simql_computedata2.txt"
#json_out_file = Path(train_txt_file).stem
#json_out_file = os.path.join(train_path,json_out_file) + '.json'
#train_txt_file = os.path.join(train_path, train_txt_file)

#converter = TextToJsonConverter('genai_training_data/train_simql_computedata2.txt', 'genai_training_data/train_simql_computedata1.json')
converter = TextToJsonConverter(train_path, train_txt_file)
converter.convert()
