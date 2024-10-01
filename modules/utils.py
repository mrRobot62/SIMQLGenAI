import re
import json 
import os
from datetime import datetime
import string
import fnmatch

def search_key_in_array_of_dicts(array_of_dicts, key_to_search, return_all=False):
    """
    Sucht nach einem Key innerhalb eines Arrays von Dictionaries und gibt die zugehörigen Werte zurück.

    :param array_of_dicts: Liste von Dictionaries, in denen gesucht werden soll.
    :param key_to_search: Der Key, der in den Dictionaries gesucht werden soll.
    :param return_all: Wenn True, werden alle Einträge, die den Key enthalten, zurückgegeben.
    :return: Liste der Werte, die dem gesuchten Key entsprechen.
    """
    results = []

    for dictionary in array_of_dicts:
        if key_to_search in dictionary:
            results.append(dictionary[key_to_search])
            if not return_all:
                break  # Wenn nur ein Treffer gewünscht ist, Schleife abbrechen

    return results


def is_key_in_array_of_dicts(array_of_dicts, key_to_search):
    """
    Sucht nach einem Key innerhalb eines Arrays von Dictionaries und gibt True zurück, wenn der Key gefunden wird.

    :param array_of_dicts: Liste von Dictionaries, in denen gesucht werden soll.
    :param key_to_search: Der Key, der in den Dictionaries gesucht werden soll.
    :return: True, wenn der Key in einem der Dictionaries vorhanden ist, sonst False.
    """
    for dictionary in array_of_dicts:
        if key_to_search in dictionary:
            return True
    return False

def is_value_in_array_of_dicts(array_of_dicts, value_to_search):
    """
    Sucht nach einem Value innerhalb eines Arrays von Dictionaries und gibt True zurück, wenn der Value gefunden wird.

    :param array_of_dicts: Liste von Dictionaries, in denen gesucht werden soll.
    :param value_to_search: Der Value, der in den Dictionaries gesucht werden soll.
    :return: True, wenn der Value in einem der Dictionaries vorhanden ist, sonst False.
    """
    for dictionary in array_of_dicts:
        if value_to_search in dictionary.values():
            return True
    return False

def get_dict_with_value(array_of_dicts, value_to_search) -> dict:
    """
    Sucht nach einem Value innerhalb eines Arrays von Dictionaries und gibt dann das dicht  zurück, wenn der Value gefunden wird.

    :param array_of_dicts: Liste von Dictionaries, in denen gesucht werden soll.
    :param value_to_search: Der Value, der in den Dictionaries gesucht werden soll.
    :return: True, wenn der Value in einem der Dictionaries vorhanden ist, sonst False.
    """
    for dictionary in array_of_dicts:
        if value_to_search in dictionary.values():
            return dictionary
    return None


def convert_to_lower_case(text, preserve_patterns = [r'(?<=[\"\'$#]\b)(.*?)(?=\b[\"\'$#])']):
    """
    Wandelt einen Text in Kleinbuchstaben (lower-case) um, behält jedoch bestimmte Inhalte unverändert,
    basierend auf den angegebenen Mustern.

    In der Regel sollen alle Bereiche die entweder in Anführungszeichen ("...") oder einfachen '...' oder
    mit $...$ gekennzeichnit sind nicht umgewandelt werden

    Diese Routine wird in der Regel genutzt um Trainingsdaten (Prompts) zu generalisieren. Gleiches gilt später
    wenn via NLP eine tatsächliche Nutzeranfrage (Prompt) gestellt wird, auch Diese wird generalisiert.

    Die Umwandlung in Kleinbuchstaben erleichert das Training

    :param text: Der Eingabetext, der umgewandelt werden soll.
    :param preserve_patterns: Eine Liste von Regex-Mustern, die nicht umgewandelt werden sollen. Default ist gesetzt
    :return: Der umgewandelte Text mit unveränderten Inhalten gemäß den übergebenen Mustern.
    """
    
    # Kombiniere alle Muster zu einem einzigen Regex-Ausdruck
    combined_pattern = '|'.join(preserve_patterns)
    #combined_pattern = preserve_patterns

    # Splitte den Text nach preserve patterns und konvertiere nur die gewünschten Teile
    result = ''
    last_end = 0

    # Iterate über alle Treffer der preserve patterns
    for match in re.finditer(combined_pattern, text):
        # Füge den Text vor dem aktuellen Match hinzu und konvertiere ihn in Kleinbuchstaben
        result += text[last_end:match.start()].lower()
        # Füge das gefundene Match unverändert hinzu
        result += match.group(0)
        # Setze den Startpunkt für den nächsten Abschnitt
        last_end = match.end()
    
    # Füge den restlichen Text nach dem letzten Match hinzu und konvertiere ihn in Kleinbuchstaben
    result += text[last_end:].lower()

    return result

def remove_duplicates_by_prompt(dicts_array, key='prompt'):
    """
    Entfernt Sätze aus einem Array von Dictionaries, die den gleichen Wert für den Key 'prompt' haben.
    
    :param dicts_array: Ein Array von Dictionaries mit dem Aufbau {'prompt': '', 'template': '', 'code': ''}.
    :return: Ein Array von Dictionaries ohne Duplikate im 'prompt'-Wert.
    """
    seen_prompts = set()  # Menge zum Speichern der bereits gesehenen 'prompt'-Werte
    unique_dicts = []     # Liste zum Speichern der eindeutigen Dictionaries
    
    for item in dicts_array:
        if 'comment' in item:
            unique_dicts.append(item)
        if key in item:
            prompt_value = item.get(key)  # Wert des 'prompt'-Keys abrufen
            if prompt_value not in seen_prompts:
                seen_prompts.add(prompt_value)  # Füge den Wert zu den gesehenen 'prompt'-Werten hinzu
                unique_dicts.append(item)       # Füge das Dictionary der Liste der eindeutigen Dictionaries hinzu

    return unique_dicts, len(seen_prompts)

# # Beispielnutzung
# input_text = 'Erstelle einen MMP "MP11" mit dem BusinessKey "MP11_tralala" und zusätzlich Messpunkte "MP1_A" und "MP2_A".'
# preserve_patterns = [r'(?<=["\'$]\b)(.*?)(?=\b["\'$])']  # Muster, das alles zwischen Anführungszeichen, einfache Anführungszeichen und Dollarzeichen selektiert

# output_text = convert_to_lower_case(input_text, preserve_patterns)
# print(output_text)  # Erwartete Ausgabe: erstelle einen mmp "MP11" mit dem businesskey "MP11_tralala" und zusätzlich messpunkte "MP1_A" und "MP2_A".

def get_timepart(pattern="%Y%m%d_%H%M%S"):
    # Aktuelles Datum und Uhrzeit inkl. Millisekunden abrufen
    now = datetime.now()
    
    # Zeit als numerischer Wert inkl. Millisekunden formatieren
    time_part = now.strftime(pattern)  #    
    return time_part


def load_text_file(path:str, file_name:str, as_array:bool=False) -> str:
    """ 
    lädt text file und gibt die Zeilen zurück. 

    :param path - Pfad zum Template
    :param file_name - Template-Name
    :return Liefert den Inhalt des Templates zurück
    """
    file_name = os.path.join(path, file_name)
    try:
        with open(file_name,'r') as file:
            if as_array:
                template = file.readlines()
            else:
                template = file.read()

    except FileNotFoundError as e:
        print(f"{file_name} - nicht verfügbar")
        raise e

    return template

def save_text_file(path:str, file_name:str, data_array):
    """ 
    Schreibt data in ein Text-File in path mit file_name

    :param path Pfad wo gespeichert wird
    :param file_name Dateiname
    :param data_array Daten die gespeichert werden

    """
    file_name = os.path.join(path, file_name)
    with open(file_name, 'w') as file:
        json.dump(data_array, file)

def replace_placeholders(template, **kwargs):
    """
    Ersetzt die Platzhalter ${wert} und ${daten} im String dynamisch, wenn sie vorhanden sind.
    Falls der Platzhalter im String vorhanden ist, aber kein entsprechender Wert übergeben wurde,
    bleibt der Platzhalter erhalten.
    
    string.Template, welches Platzhalter im Format ${platzhalter} unterstützt.
    safe_substitute(): Diese Methode ersetzt nur die vorhandenen Platzhalter, ohne Fehler zu werfen, 
    wenn ein Platzhalter keinen entsprechenden Wert hat. Fehlende Platzhalter bleiben im String erhalten.

    :param template: Der String, der Platzhalter enthält.
    :param kwargs: Die zu ersetzenden Werte für die Platzhalter.
    :return: Der String mit den ersetzten Werten.
    """
    # Erstelle eine Template-Instanz
    template_obj = string.Template(template)
    
    # Ersetze Platzhalter, wobei fehlende Platzhalter unverändert bleiben
    return template_obj.safe_substitute(kwargs)

def remove_entries_by_pattern(entry_set, regex_patterns=None, wildcard_patterns=None):
    """
    Entfernt Einträge aus einem Set, die entweder einem regulären Ausdruck oder Wildcards entsprechen.
    
    :param entry_set: Set mit Einträgen.
    :param regex_patterns: Liste von regulären Ausdrücken.
    :param wildcard_patterns: Liste von Wildcard-Strings (wie "AUTO_*").
    :return: Set ohne die Einträge, die den Mustern entsprechen.
    """
    # Wenn kein Muster vorhanden ist, gib das ursprüngliche Set zurück
    if not regex_patterns and not wildcard_patterns:
        return entry_set

    # Kompiliere die regulären Ausdrücke
    compiled_regexes = [re.compile(pattern) for pattern in regex_patterns] if regex_patterns else []
    
    # Führe das Filtern durch
    filtered_set = set()
    for entry in entry_set:
        # Überprüfe auf reguläre Ausdrücke
        if any(regex.match(entry) for regex in compiled_regexes):
            continue
        
        # Überprüfe auf Wildcard-Muster
        if any(fnmatch.fnmatch(entry, pattern) for pattern in wildcard_patterns or []):
            continue
        
        # Behalte den Eintrag, wenn er kein Muster trifft
        filtered_set.add(entry)
    
    return filtered_set

