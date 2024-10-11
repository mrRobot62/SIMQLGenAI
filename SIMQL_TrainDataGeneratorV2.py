import argparse
import sys
import os 
from pathlib import Path
import json
import re
import random
import string

from datetime import datetime
from modules.ConvertPromptToJson import ConvertPromptToJSON
from modules.utils import *
from prettytable import PrettyTable
import time

class TraindataGeneratorV2:
    mmp_alias       = ["MMP1234", "MMP2345", "MMP3456", "MMP5678", "MMP7890","MMP100","MMP200","MMP300","MMP400","MMP500"]
    vmp1            = ["vTempA1","vTempA2","vTempA3","vTempA4","vTempA5", "vMP1"]
    vmp2            = ["vTempB1","vTempB2","vTempB3","vTempB4","vTempB5", "vMP2"]
    vmp3            = ["vTempC1","vTempC2","vTempC3","vTempC4","vTempC5", "vMP3"]
    vmp4            = ["vTempD1","vTempD2","vTempD3","vTempD4","vTempD5", "vMP4"]
    vmp5            = ["vTempE1","vTempE2","vTempE3","vTempE4","vTempE5", "vMP5"]
    vmp6            = ["vTempF1","vTempF2","vTempF3","vTempF4","vTempF5", "vMP6"]
    mp1             = ['MP_Name_A1','MP_Name_A2','MP_Name_A3','MP_Name_A4','MP_Name_A5','MP_Name_A6', ]
    mp2             = ['MP_Name_B1','MP_Name_B2','MP_Name_B3','MP_Name_B4','MP_Name_B5','MP_Name_D6', ]
    mp3             = ['MP_Name_C1','MP_Name_C2','MP_Name_C3','MP_Name_C4','MP_Name_C5','MP_Name_C6', ]
    mp4             = ['MP_Name_D1','MP_Name_D2','MP_Name_D3','MP_Name_D4','MP_Name_D5','MP_Name_D6', ]
    mp5             = ['MP_Name_E1','MP_Name_E2','MP_Name_E3','MP_Name_E4','MP_Name_E5','MP_Name_E6', ]
    mp6             = ['MP_Name_F1','MP_Name_F2','MP_Name_F3','MP_Name_F4','MP_Name_F5','MP_Name_F6', ]
    var1            = ['vTmpA1', 'vTmpA2','vTmpA3','vTmpA4','vTmpA5']
    var2            = ['vTmpB1', 'vTmpB2','vTmpB3','vTmpB4','vTmpB5']
    var3            = ['vTmpC1', 'vTmpC2','vTmpC3','vTmpC4','vTmpC5']
    var4            = ['vTmpD1', 'vTmpD2','vTmpD3','vTmpD4','vTmpD5']
    var5            = ['vTmpE1', 'vTmpE2','vTmpE3','vTmpE4','vTmpE5']
    var6            = ['vTmpF1', 'vTmpF2','vTmpF3','vTmpF4','vTmpF5']
    var_result      = ['vResult', 'vErgebnis','vData','vRes','vSave']
    refdates1       = ['CREF', 'CREF-1', 'CREF-2']
    refdates2       = ['QREF','QREF-1','QREF-2']
    refdates3       = ['HREF']
    refdates4       = ['YREF', 'YREF-1','YREF-2']
    refdate_iqr     = ['CREF', 'CREF-1', 'CREF-2']
    ranges          = ['LATEST','FIRST','ALL']
    qlevels         = ['AT', 'LAT', 'U4', 'UF']
    environments    = ['A360_TUC1','A360_TUC2','A360_TUC3','A360_TUC4','A360_TUD1','BIAP_TUC1','BIAP_TUC2','BIAP_TUD1','FRDWH_TUC1']
    math_operations = ["SUM", "MAX", "MINUS", "MULT", "AGG","STDEV", "DIV","PLUS"]


    def __init__(self, args):
        """
        Initialisiert den TraindataGeneratorV2 mit den angegebenen Argumenten.

        :param args: Die Kommandozeilenargumente.
        """
        self.path_prompts = args.path_prompts
        self.path_templates = args.path_templates
        self.out_path = args.out_path
        self.out_file = None
        #self.use_short_prompts = args.s
        #self.use_complex_prompts = args.c
        self.num_records = args.n
        self.random_prompts = (10 if args.random_prompts > 10 else  args.random_prompts)
        self.prompt_suffix = args.prompt_suffix
        self.prompt_prefix = args.prompt_prefix
        self.prompt_file = args.prompt_file
        self.read_all = args.read_all
        self.use_lowercase = args.use_lowercase

        if self.read_all:
            self.prompt_file = None
        if self.read_all == False and self.prompt_file is None:
            raise ValueError("Es wurde kein prompt file angegeben. Parameter --prompt_file")

        self._prompts = []      # Liste aller geladenen Prompts
        self._templates = []    # Liste aller geladenen Templates (SIMQL)
        self._code = []         # 

        self.converter = ConvertPromptToJSON(self.path_prompts)

        # Weitere Initialisierungen oder Methodenaufrufe können hier hinzugefügt werden

    @property
    def getNumRecords(self):
        return self.num_records
    
    def _load_templates_from_directory(self, directory_path:str, suffix='.txt', prefix:str='template', this_file:str=None):
        """ 
        Lädt alle Template-Files from directory_path und erzeugt ist liste von
        dicts.
        Aufbau:
        [ {"key" : template_name, 'code':source_code}, ...]
        """
        combined_data = []
        template_files = []
        try:
            # Überprüfen, ob der angegebene Pfad ein Verzeichnis ist
            if not os.path.isdir(directory_path):
                print(f"Der angegebene Pfad '{directory_path}' ist kein Verzeichnis.")
                return combined_data
            for filename in os.listdir(directory_path):
                if filename.endswith(suffix) and (prefix is None or filename.startswith(prefix)):
                    if this_file is not None and filename != this_file:
                        continue
                    file_path = os.path.join(directory_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_content = file.read()  # Liest die Datei 
                            tname, _ = os.path.splitext(filename)
                            combined_data.append({
                                "key" : tname,
                                "code": file_content
                            })
                            template_files.append(tname)
                    except Exception as e:
                        print(f"Fehler beim Lesen der Template-Datei {filename}: {e}")

        except Exception as e:
            print(f"Fehler beim Durchsuchen des Verzeichnisses: {e}")

        return combined_data, template_files           

    def _load_files_from_directory(self, directory_path, suffix, prefix:str=None, this_file:str=None):
        """
        Lädt Dateien aus einem Verzeichnis basierend auf einem angegebenen Suffix und optionalen Präfix.
        Führt den Inhalt aller passenden Dateien in einer Liste zusammen. Jede Zeile ist ein Eintrag in der Liste

        :param directory_path: Pfad des Verzeichnisses, aus dem die Dateien geladen werden sollen.
        :param suffix: Das Suffix (z.B. '.txt'), nach dem die Dateien gefiltert werden sollen.
        :param prefix: (Optional) Die ersten Zeichen des Dateinamens, nach denen gefiltert werden soll.
        :return: Eine Liste mit den Inhalten aller passenden Dateien.
        """
        combined_data = []
        used_files=[]
        try:
            # Überprüfen, ob der angegebene Pfad ein Verzeichnis ist
            if not os.path.isdir(directory_path):
                print(f"Der angegebene Pfad '{directory_path}' ist kein Verzeichnis.")
                return combined_data

            # Durchsuchen des Verzeichnisses nach Dateien mit dem angegebenen Suffix und optionalem Präfix
            for filename in os.listdir(directory_path):
                if filename.endswith(suffix) and (prefix is None or filename.startswith(prefix)):
                    if this_file is not None and filename != this_file:
                        continue
                    file_path = os.path.join(directory_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_content = file.readlines()     # liest zeilenweise !
                            combined_data.extend(file_content)  # Fügt den Inhalt zur Liste hinzu
                            used_files.append(os.path.basename(file_path))
                    except Exception as e:
                        print(f"Fehler beim Lesen der Datei {filename}: {e}")

        except Exception as e:
            print(f"Fehler beim Durchsuchen des Verzeichnisses: {e}")

        return combined_data, used_files



    def load(self, save_to_file:bool=False) -> list:
        """ 
        Eine oder mehrere PROMPT-Files. Alle PROMPTFiles müss dem angegeben PREFIX und SUFFIX entsprechend.
        Ist this_file explizit gesetzt wird nur dieses PROMPT_FILE gelesen, ansonsten wird das aktuelle Verzeichnis
        gescannt und alle PROMPTSs gelesen

        Die Methode erzeugt eine JSON-Struktur aus den PROMPT-Dateien.
        :read_all default True, alle Prompt Dateien aus dem Folder werden geladen.
        :return self._prompts
        """
        prompt_raw_data, used_files = self._load_files_from_directory(self.path_prompts, self.prompt_suffix, self.prompt_prefix, self.prompt_file)

        prompt_converted = self.converter.load_and_convert(raw_data=prompt_raw_data, file_name=None, save_to_file=save_to_file)

        if prompt_converted is None or len(prompt_converted) == 0:
            raise RuntimeWarning("Es wurde keine Prompts geladen. Bitte Pfad oder Dateien prüfen. Abbruch")

        #
        # Umsetzung von Synonymen bevor tatsächliche Trainingsdaten generiert werden
        #


        return prompt_converted

    def load_templates(self):
        """ 
        lädt alle Templates in eine JSON-Struktur
        
        :return template_json Inhalt der Templates als JSON-Struktur
        :return template_files Liste der geladenen Templates
        """
        template_json, template_files = self._load_templates_from_directory(self.path_templates, '.txt', 'template_simql')
        return template_json, template_files
    
    def generate_data(self, prompt_converted:list, template_data:list, template_names:list, save_to_file=False, ):
        """
        Implementiert die Logik zur Generierung der Trainingsdaten.
        Die über den parameter -n übergebene Zahl ist ein Multiplikator zu Generierung von Trainingssätzen.

        Das Pythonmodul "prompt_generator.py" erstellt dynamisch basierend auf eine Input-Json-Datei prompts mit Platzhaltern.
        Die Anzahl der prompts berechnet sich aus den Möglichkeiten die innerhalb der JSON definiert wurden.

        Die daraus generierten Prompts werden nun mit dem -n Multiplikator multipliziert und für jeden
        dieser prompts werden n Prompts mit unterschiedlichen Platzhalter-Werten generiert.

        bei 300 dynamischen Prompts und einem Multiplikator von 10 werden 3000 Prompts generiert

        :param prompt_converted Eine Liste von konvertierten Prompts in einer JSON-Struktur
        :param templates Eine Liste von Templates in einer JSON-Struktur
        :save_to_file Default True, speichert alls Jsons als zwischendatei lokal (nur nützlich zur Prüfung, falls ein Fehler auftritt)
        """
        i = idx = 0
        examples = []   # Array für Trainingsdatenstrukturen

        print("Generierung der Trainingsdaten läuft...")
        size = int(self.num_records)

        self.out_file = self.__generate_filename(int(self.num_records))
        self.out_file = os.path.join(self.out_path, self.out_file)
        text = prompt_text = code = template_name = None
        used_templates = set()

        for _ in range(size):
            for prompt in prompt_converted:
                if None in prompt:
                    continue
                prompt_text = prompt['prompt']

                prompt_template = prompt['template']
                prompt_code = prompt['code']
                dsl = None
                if len(prompt_template) > 0:
                    template_dict = get_dict_with_value(template_data, prompt_template)
                    template_name = prompt['template'] 
                    template_file = os.path.join(self.path_templates,template_name + '.txt')
                    if  os.path.exists(template_file) == False:
                        print(f"Ungültiges Template '{template_name}' für Prompt '{prompt[:15]}...'")
                        print(f"Template-File '{template_file}' nicht verfügbar'")
                        continue

                    used_templates.add(template_name)
                    template_dict = get_dict_with_value(template_data, template_name)
                    prompt_code = template_dict['code']

                mmp_alias = random.choice(self.mmp_alias)
                mmp_name = self.__generate_random_string(10, mmp_alias + '_')
                mp1 = random.choice(self.mp1)
                mp2 = random.choice(self.mp2)
                mp3 = random.choice(self.mp3)
                mp4 = random.choice(self.mp4)
                qlevel  = random.choice(self.qlevels)
                refdate1 = random.choice(self.refdates1)
                refdate2 = random.choice(self.refdates2)
                refdate3 = random.choice(self.refdates3)
                environment = random.choice(self.environments)
                data_range = random.choice(self.ranges)
                math_operations = random.choices(self.math_operations)

                #
                # Prompt vorbereiten
                e=0
                try:
                    e="PROMPT"
                    text = prompt_text.format(
#                        mmp_alias       = mmp_alias,
                        mmp_name        = mmp_name,
                        mp1             = mp1,
                        mp2             = mp2,
                        mp3             = mp3,
                        mp4             = mp4,
                        qlevel          = qlevel,
                        data_range      = data_range,
                        environment     = environment,
                        math            = math_operations,
                        refdate1        = refdate1,
                        refdate2        = refdate2,

                    )

                    #
                    # falls eine Normierung in Kleinbuchstaben stattfinden soll.
                    #
                    # Wichtig: wenn die Trainingsdaten in Kleinbuchstaben normiert wurden, dann muss das auch während der NLP-Prozessierung mit 
                    #           echten Anfragen durchgeführt werden !
                    #
                    if self.use_lowercase:
                        text = convert_to_lower_case(text)

                except (KeyError, ValueError) as e:
                    err_place = "Template: " + prompt["prompt"]
                    print(f"\n WARINING:Fehler in {e}: Ersetzung einer dynamischen Variable im PROMPT nicht möglich. Error: {e}")
                    print(f"\n Gefunden in '{err_place}'")
                    # fehler ignorieren und weiter machen. Dieses Prompt wird ignoriert
                    continue     
                except Exception as e:
                    print(f"Unbekannter Fehler bei der Verarbeitung von dynamischen Variablen: Error: {e}")
                    continue    
                try:             
                    e='CODE'
                    #
                    # Code vorbereiten

                    dsl = prompt_code.format(
                        mmp_alias       = self._build_random_mmp_alias(),
                        mmp_name        = mmp_name,
                        mp1             = mp1,
                        mp2             = mp2,
                        mp3             = mp3,
                        mp4             = mp4,
                        qlevel          = qlevel,
                        data_range      = data_range,
                        environment     = environment,
                        math            = math_operations,
                        refdate         = refdate1,
                    )         
                except (KeyError, ValueError) as e:
                    err_place = "Template:" + prompt["template"] + "' oder Code: '" + prompt["code"] + ""
                    print(f"\n WARINING:Fehler in {e}: Ersetzung einer dynamischen Variable im CODE nicht möglich. Error: {e}")
                    print(f"\n Gefunden in '{err_place}'")
                    # fehler ignorieren und weiter machen. Dieses Prompt wird ignoriert
                    continue  
                except Exception as e:
                    print(f"Unbekannter Fehler bei der Verarbeitung von dynamischen Variablen: Error: {e}")
                    continue              
                              
                examples.append(
                    {'text' : text, 'code':dsl}
                )

                if (idx % 100) == 0:
                    i=i+1
                    print(f"({_:3d})[{idx:5d}], ", end='')
                    if i % 10 == 0:
                        print()
                        i=0
                idx = idx+1

        #
        # Für jeden Prompt ist der dazugehörige Code zugeordnet worden und enthält nun mögliche Demo-Daten
        #
        # Im nächsten Schritt werden die Trainingsdaten als JSON gespeichert
        self.out_file = self.__generate_filename(idx)
        self.out_file = os.path.join(self.out_path, self.out_file)
        #
        # Für Trainingsdaten sollten die promptes einzigartig (unique) sein, daher wird nun
        # das komplette array nochmals durchforstet nach doppelten Einträgen
        print(f"\n\ngenerierte Anzahl Prompts:  '{len(examples)}'")
        examples, number_unique_prompts = remove_duplicates_by_prompt(dicts_array=examples, key='text')
        print(f"Unique Prompts:             '{number_unique_prompts}'")
        
        # all_tokens = set()      # set verwenden um duplikate zu vermeiden
        # #
        # # Prompts als Tokens aufnehmen
        # # SIMQL-Code als Tokens aufnehmen
        # for text in examples:
        #     words = text['text'].split()
        #     codes = text['code'].split()
        #     all_tokens.update(words)
        #     all_tokens.update(codes)

        # all_tokens = sorted(list(remove_entries_by_pattern(
        #     all_tokens, 
        #     wildcard_patterns=["AUTO*","MMP*_*",".", "#", "#all", "#save"],
        #     regex_patterns=[r"\"MMP\d+_.+\"", r"\'MMP\d+_.+\'"]  
        # )))
        # all_tokens = sorted(list(remove_entries_by_pattern(
        #     all_tokens, 
        #     regex_patterns=[r"\"", r"\'"]  
        # )))
        # save_text_file('./', 'additional_tokens.txt', all_tokens)

        #print (f"Neue Tokens basierend auf PROMPTS & Code: {len(all_tokens)}")    
        try:
            with open(self.out_file, 'w') as json_file:
                json.dump(examples, json_file, indent=2)
        except Exception as err:
            print(f"Fehler beim Schreiben der Trainingsdaten-Datei '{self.out_file}'. Fehler {err}")

        print()
        tbl = PrettyTable()
        tbl.field_names = ['Data', os.path.basename(self.out_file)]
        tbl.add_row(['path', os.path.dirname(self.out_file)])
        tbl.add_row(['examples', idx])
        tbl.add_row(['unique', number_unique_prompts])
        tbl.add_row(['from prompts', len(prompt_converted)])
        tbl.add_row(['available templates', len(template_names)])
        tbl.add_row(['used templates', len(used_templates)])
        print(tbl)
        tbl = PrettyTable()
        tbl.field_names = ['used Templates']
        for t in used_templates : tbl.add_row([t])
        print(f"\n{tbl}")


        pass

    def __generate_filename(self, num_records:int) -> str:
        """
        Erstellt einen Dateinamen im Format train_data_yyyymmdd_hhmm_num.json.

        :param num_records: Anzahl der Datensätze, als integer.
        :return: Der generierte Dateiname als String.
        """
        # Aktuelles Datum und Uhrzeit abrufen
        now = datetime.now()
        date_part = now.strftime("%Y%m%d")  # Format: yyyymmdd
        time_part = now.strftime("%H%M")    # Format: hhmm

        # Anzahl der Datensätze als 7-stellige Zahl mit führenden Nullen
        num_part = f"{num_records:07d}"

        # Dateiname zusammenbauen
        filename = f"train_data_{date_part}_{time_part}_{num_part}.json"
        return filename

    def __generate_random_string(self, length:int, prefix:str="") -> string:
        """
        Generiert eine zufällige Buchstabenkombination mit angegebenem Präfix und konvertiert sie in Großbuchstaben.

        :param length: Länge der zufälligen Buchstabenkombination.
        :param prefix: Präfix, das vor der zufälligen Buchstabenkombination hinzugefügt wird.
        :return: Der generierte String in Großbuchstaben.
        """
        # Erstellen einer zufälligen Buchstabenkombination der angegebenen Länge
        random_letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

        # Zusammenführen von Präfix und zufälligen Buchstaben
        result = f"{prefix}{random_letters}"
        
        return result

    def _build_random_mmp_alias(self, suffix="MMP", prefix='AUTO'):
        """
        Erzeugt einen MMP Alias Namen bestehend aus SUFFIX_epoch_time_ms_PREFIX
        
        :return: Der generierte Alias-String.
        """

        # Aktuelles Datum und Uhrzeit inkl. Millisekunden abrufen
        now = datetime.now()
        
        # Zeit als numerischer Wert inkl. Millisekunden formatieren
        rnd = int(random.uniform(100,9999))
        time_part = now.strftime("%Y%m%d%H%M%S")  # yyyymmddhhmmss
        
        # Zusammenbau des Alias-Strings

        epoch_timestamp_milliseconds = int(time.time() * 1000)

        # Zusammenbau des Alias-Strings
        #alias = f"{suffix}_{epoch_timestamp_milliseconds}_{int(rnd)}_{prefix}"
        alias = f"{prefix}_{time_part}_{rnd:04d}_{suffix}"
        
        return alias


def parse_arguments():
    """
    Parsed die Kommandozeilenargumente und gibt sie zurück.
    """
    parser = argparse.ArgumentParser(description="Trainingsdatengenerator V2")
    parser.add_argument('--path_prompts', required=True, help='Pfad zu den Prompts')
    parser.add_argument('--path_templates', required=True, help='Pfad zu den Templates')
    parser.add_argument('--prompt_suffix', default=".txt", help='Suffix der ladefähigen Eingabe-Prompts. Default ist .txt')
    parser.add_argument('--prompt_prefix', default='prompt', required=False, help='Default startet der prompt-filename immer mit prompt_xxxxx.suffix')
    parser.add_argument('--prompt_file',required=False, help='verwende ausschließlich das angegebene Prompt')
    parser.add_argument('--read_all', action='store_true', help='verwende diese Prompts')
    parser.add_argument('--out_path', required=True, help='Ausgabepfad für die Trainingsdaten')
    parser.add_argument('--random_prompts', default=5, help='Anzahl Traingingssätze berechnet sich aus Anzahl Prompts * random_prompts')
    parser.add_argument('--use_lowercase', action='store_true', default=True, help='Prompt wird in Kleinbuchstaben umgewandelt (Mit Ausnahmen!!!)')
    parser.add_argument('-n', required=True, help='Multiplikator für Traingingssätze berechnet sich aus Anzahl pre-generierten prompts * multiplikator')
    parser.add_argument('-v', action='count', help='Anzahl Traingingssätze berechnet sich aus Anzahl Prompts * random_prompts')
    # entweder man übergibt ein Prompt-File oder man liest alle Prompt-Files. Die Datei(en) müssen im Verzeichnis --path_prompts liegen
    #group_prompts = parser.add_mutually_exclusive_group(required=True)
    #group_prompts.add_argument('--read_all', action='store_true', help='verwende diese Prompts')


    return parser.parse_args()

def main():
    args = parse_arguments()
    
    try:
        generator = TraindataGeneratorV2(args)
        #
        # Alle TXT-Prompts werden gelesen und in eine JSON-Struktur unmgewandelt
        # 
        prompt_converted = generator.load()

        #
        # Alle SIMQL-Templates laden. Wird für die Code-Ersetzung benötigt
        template_data, templates_name = generator.load_templates()

        #
        # Erzeugen der tatsächlchen Trainingsdatensätze. Speicherung als JSON-Datei
        generator.generate_data(prompt_converted, template_data, templates_name)
    except ValueError as e:
        print(f"Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
