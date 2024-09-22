import json
import re

class PhraseMapper:
    def __init__(self, phrase_mappings=None, json_file=None):
        """
        Initialisiert den PhraseMapper mit einem Wörterbuch von Phrasen und deren Ersetzungen
        oder lädt die Mappings aus einer JSON-Datei.
        
        :param phrase_mappings: Ein Wörterbuch, das Phrasen (Schlüssel) auf ihre Ersetzungen (Werte) abbildet.
        :param json_file: Pfad zu einer JSON-Datei, die Phrasen-Mappings enthält.
        """
        if json_file:
            self.phrase_mapping = self.load_mappings_from_json(json_file)
        elif phrase_mappings:
            self.phrase_mapping = phrase_mappings
        else:
            self.phrase_mapping = {}
        
        # Sortiere Phrasen nach Länge, damit längere Phrasen zuerst ersetzt werden
        self.sorted_phrases = sorted(self.phrase_mapping.keys(), key=len, reverse=True)

    def load_mappings_from_json(self, json_file):
        """
        Lädt die Phrasen-Mappings aus einer JSON-Datei.
        
        :param json_file: Pfad zur JSON-Datei.
        :return: Ein Wörterbuch mit Phrasen-Mappings.
        """
        try:
            with open(json_file, 'r') as file:
                mappings = json.load(file)
            return mappings
        except FileNotFoundError:
            print(f"Die Datei {json_file} wurde nicht gefunden.")
            return {}
        except json.JSONDecodeError:
            print(f"Die Datei {json_file} enthält kein gültiges JSON.")
            return {}

    def map_phrases(self, text):
        """
        Ersetzt Phrasen im gegebenen Text durch die spezifizierten Ersetzungen.
        
        :param text: Eingabetext, in dem Phrasen ersetzt werden sollen.
        :return: Text mit ersetzten Phrasen.
        """
        # Ersetzen von Phrasen
        for phrase in self.sorted_phrases:
            text = re.sub(rf'\b{re.escape(phrase)}\b', self.phrase_mapping[phrase], text)
        return text
 