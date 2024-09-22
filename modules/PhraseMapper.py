# phrase_mapper.py

import json

class PhraseMapper:
    def __init__(self, mapping_file):
        """
        Initialisiert den PhraseMapper und lädt Phrasen-Mappings aus einer JSON-Datei.
        
        :param mapping_file: Pfad zur JSON-Datei mit Phrasen-Mappings.
        """
        self.mapping_file = mapping_file
        self.phrase_mapping = self.load_mappings_from_json(mapping_file)

    @property
    def getCountPhrases(self):
        """ 
        gibt die Anzahl der geladenen Phrase-Mappings zurück
        :return Anzahl der Phrasen
        """
        return len(self.phrase_mapping)
    
    def load_mappings_from_json(self, json_file):
        """
        Lädt Phrasen-Mappings aus der angegebenen JSON-Datei.
        
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

    def add_mappings_to_target_array(self, target_data):
        """ 
        fügt die geladenen Phrasen-Mappings in die Zielstruktur. 

        :param target_data: Phrasen werden in diese Struktur übernommen
        :return target_data - Rückgabe der Struktur
        """
        # Erstelle neue Einträge für jedes Mapping
        new_entries = [{"text": phrase, "code": code} for phrase, code in self.phrase_mapping.items()]
        
        # Füge die neuen Einträge hinzu
        target_data.extend(new_entries)

        return target_data


    def add_mappings_to_target_file(self, target_file):
        """
        Fügt die geladenen Phrasen-Mappings der Ziel-JSON-Datei hinzu.
        
        :param target_file: Pfad zur Ziel-JSON-Datei, die ein Array von Dictionaries enthält.
        """
        try:
            # Lade vorhandene Daten aus der Ziel-JSON-Datei
            with open(target_file, 'r') as file:
                target_data = json.load(file)
            
            # Erstelle neue Einträge für jedes Mapping
            new_entries = [{"text": phrase, "code": code} for phrase, code in self.phrase_mapping.items()]
            
            # Füge die neuen Einträge hinzu
            target_data.extend(new_entries)
            
            # Speichere die aktualisierten Daten zurück in die Datei
            with open(target_file, 'w') as file:
                json.dump(target_data, file, indent=2)
            
            print(f"{len(new_entries)} Einträge wurden der Datei {target_file} hinzugefügt.")
        except FileNotFoundError:
            print(f"Die Datei {target_file} wurde nicht gefunden.")
        except json.JSONDecodeError:
            print(f"Die Datei {target_file} enthält kein gültiges JSON.")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")


# Beispielhafte Verwendung
if __name__ == "__main__":
    # Pfad zur Mapping-Datei und Ziel-JSON-Datei
    mapping_json_path = 'genai_training_data/nlp_data/phrase_mappings.json'
    target_json_path = 'genai_training_data/simql_prompts_014178.json'
    
    # Beispiel-JSON-Datei-Inhalt für `phrase_mappings.json`:
    # {
    #     "aktueller Stichtag": "refdate=CREF",
    #     "dieser Stichtag": "refdate=CREF",
    #     "letzter Stichtag": "refdate=CREF-1",
    #     "aggregiere Daten": "math=AGG"
    # }

    # Erstelle eine Instanz von PhraseMapper
    phrase_mapper = PhraseMapper(mapping_json_path)
    
    # Füge die Mappings zur Ziel-JSON-Datei hinzu
    phrase_mapper.add_mappings_to_target_file(target_json_path)
