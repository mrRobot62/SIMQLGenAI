import random
import re
import json
import os
from pathlib import Path
from modules.PhraseMapper import PhraseMapper
from modules.PromptToJsonConverter import PromptToJsonConverter
from modules.utils import *
from prettytable import PrettyTable

class TrainDataGenerator:
    mmp_alias       = ["MMP1234", "MMP2345", "MMP3456", "MMP5678", "MMP7890","MMP100","MMP200","MMP300","MMP400","MMP500","MMP600"]
    mmp_name        = ["MMP_NAME_1234", "MMP_NAME_2345", "MMP_NAME_3456", "MMP_NAME_5678", "MMP_NAME_7890","MMP_NAME_100","MMP_NAME_200","MMP_NAME_300","MMP_NAME_400","MMP_NAME_500","MMP_NAME_600"]
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

    def __init__(self, template_path:str, nlp_file:str, nlp_phrases_file:str, out_path:str, convertToAbsolutePath:bool=True):
        if convertToAbsolutePath:
            self._template_path = os.path.join(os.getcwd(), template_path)
            self._nlp_file = os.path.join(os.getcwd(), nlp_file)
            self._nlp_phrases_file = os.path.join(os.getcwd(), nlp_phrases_file)
            self._out_path = os.path.join(os.getcwd(), out_path)
        else:
            self._template_path = template_path
            self._nlp_file = nlp_file
            self._out_path = out_path
        

        self._code = []
        self._prompts = []



    def generate_train_data(self, size:int):
        if len(self._prompts) == 0:
            print("Keine NLP Prompts geladen. Nutze 'load_nlp_data'")
            exit(1)
        if len(self._code) == 0:
            print("Keine SIMQL-Template files gefunden. Nutze 'load_templates'")
        examples = []
        nPrompts = len(self._prompts)
        size = size / nPrompts
        i=id = 0
        used_templates = []
        #
        # insgesamt sollen 'size' Trainingsdatensätze generiert werden
        # size ist die Gesamtsumme bezogen auf Trainingsdatensätze über alle Muster-Prompts
        for _ in range(int(size)+1):
            #print(f"Block ({_:3d})")
            #
            # für jeden Prompt werden nun die Variablen gefüllt und zusätzlich den dazugehörige Template-Code
            # ebenfalls mit den Variablen-Werten gefüllt
            # diese Key/Value Paar wird anschließend in einer Liste gespeichert
            for prompt in self._prompts:
                template_name = prompt['template']
                prompt_text = prompt['text']
                if template_name not in used_templates:
                    used_templates.append(template_name)
                #
                # zur Sicherheit prüfen ob für das Prompt auch ein Template verfügbar ist, ansonsten das Prompt ignorieren
                if is_value_in_array_of_dicts(self._code, template_name) == False:
                    print(f"!!!!!! ---- für dieses Prompt steht kein Template ('{template_name}') zur Verfügung ---- !!!!!")
                    continue
            
                #
                # Variablen die sowohl im prompt als auch im template verwendet werden
                mmp_alias   = random.choice(self.mmp_alias)
                mp1         = random.choice(self.mp1)
                mp2         = random.choice(self.mp2)
                mp3         = random.choice(self.mp3)
                mp4         = random.choice(self.mp4)
                mp5         = random.choice(self.mp5)
                mp6         = random.choice(self.mp6)
                refdate_t1  = random.choice(self.refdates1)
                refdate_t2  = random.choice(self.refdates2)
                refdate_t3  = random.choice(self.refdates3)
                refdate_c1   = f"refdates=[\"{refdate_t1}\"]"
                refdate_c2   = f"refdates=[\"{refdate_t2}\"]"
                refdate_c3   = f"refdates=[\"{refdate_t3}\"]"
                math_t       = random.choice(self.math_operations)
                math_c        = f"math={math_t}"
                qlevels_t     = random.choice(self.qlevels)
                qlevels_c     = f"qualityLevel=\"{qlevels_t}\""
                environment_t = random.choice(self.environments)
                environment_c = f"environment=\"{environment_t}\""
                data_range_t  = random.choice(self.ranges)
                data_range_c  = f"range={data_range_t}"
                #
                # Prompt vorbereiten
                try:
                    text = prompt_text.format(
                        mmp_alias   = mmp_alias,
                        mp1         = mp1,
                        mp2         = mp2,
                        mp3         = mp3,
                        mp4         = mp4,
                        mp5         = mp5,
                        mp6         = mp6,
                        refdate1    = refdate_t1,
                        refdate2    = refdate_t2,
                        refdate3    = refdate_t3,
                        math        = math_t,
                        qlevel      = qlevels_t,
                        environment = environment_t,
                        data_range  = data_range_t,
                    )
                except ValueError as err:
                    print(f"!!!! ---- ERROR in Prompt-Text '{prompt_text}'. Error: {err}")
                    continue            
                #
                # ersetze nun zu jedem template-code die Variablen durch Werte
                template_dict = get_dict_with_value(self._code, template_name)
                # DSL vorbereiten
                try:
                    dsl = template_dict["code"].format(
                        #
                        # Template mit Daten bestücken
                        mmp_alias   = mmp_alias,
                        mmp_name    = random.choice(self.mmp_name),
                        mp1         = mp1,
                        mp2         = mp2,
                        mp3         = mp3,
                        mp4         = mp4,
                        mp5         = mp5,
                        mp6         = mp6,
                        refdate1    = refdate_c1,
                        refdate2    = refdate_c2,
                        refdate3    = refdate_c3,
                        math        = math_c,
                        qlevel      = qlevels_c,
                        environment = environment_c,
                        data_range  = data_range_c,
                    )
                except ValueError as err:
                    print(f"!!!! ---- ERROR in DSL-Template '{template_name}'. Error: {err}")
                    continue

                #print (f"CODE:\n{dsl}")
                examples.append({
                    'text' : text,
                    'code' : dsl.strip()
                })
                
                if (id % 100) == 0:
                    i=i+1
                    print(f"({_:3d})[{id:5d}], ", end='')
                    if i % 10 == 0:
                        print()
                        i=0
                id = id+1
            pass # for prompt

        phraseMapper = PhraseMapper(self._nlp_phrases_file)
        examples = phraseMapper.add_mappings_to_target_array(examples)
        rows = len(examples)
        rowsPhrases = phraseMapper.getCountPhrases

        #
        # speichere alle Ergebniss in einer JSON-Datei
        self._out_file = os.path.basename(self._nlp_file).split('.')[0] +f"_{rows:06d}.json"
        self._out_file = os.path.join(self._out_path, self._out_file)
        try:
            with open(self._out_file, 'w') as json_file:
                json.dump(examples, json_file, indent=2)
        except Exception as err:
            print(f"Fehler beim Schreiben der Examples-Datei. Fehler {err}")

        print()
        tbl = PrettyTable()
        tbl.field_names = ['Data', os.path.basename(self._out_file)]
        tbl.add_row(['path', os.path.dirname(self._out_file)])
        tbl.add_row(['examples', rows])
        tbl.add_row(['phrasses', rowsPhrases])
        tbl.add_row(['prompts', len(self._prompts)])
        tbl.add_row(['available templates', len(self._code)])
        tbl.add_row(['used templates', len(used_templates)])
        print(tbl)
        tbl = PrettyTable()
        tbl.field_names = ['used Templates']
        for t in used_templates : tbl.add_row([t])
        print(f"\n{tbl}")
        pass #for size

    def load_nlp_data(self, nlp_file:str=None) -> list:
        """
        lädt NLPDaten (prompts) inkl. dem Verweis welches DSL-Template zu diesem Prompt passt.
        Speichert die Daten in einem JSON-Array in der Form. Nutzt das Modul TextToJsonConverter
        [
            {'text':'<prompt>', 'template':'<template-name>'}
        ]
        :param nlp_file: wenn angegeben, überschreibt er den self._nlp_file name und lädt diese Datei

        """
        if nlp_file is None:
            nlp_file = self._nlp_file
        promptConverter = PromptToJsonConverter(nlp_file)
        promptConverter.import_text_file()
        self._prompts = promptConverter.get_json_data
        return self._prompts

    def load_templates(self, template_path:str=None) -> list:
        """ 
        lädt alle verfügbaren Templates und speichert diese ein einer JSON-Struktur.
        Strukturaufbau: {'template':'<name>', 'code':'''simql-template-code'''}
        """
        self._code = []
        if template_path is None:
            template_path = self._template_path
        template_files = self.get_template_files_with_suffix(template_path)
        for _ in template_files:
            with open(_, 'r', encoding='utf-8') as f:
                code = f.read()
            key_value = os.path.splitext(os.path.basename(_))[0]
            template = {'template':key_value, 'code':code}
            self._code.append(template)
            print(f"Read template '{key_value}'")
        return self._code


    def save_to_json(self):
        pass 


    def get_template_files_with_suffix(self, directory_path:str=None, suffix:str='txt', appendPath:bool=True):
        """
        Liest alle Dateien aus einem bestimmten Verzeichnis mit einem bestimmten Suffix und gibt die Dateinamen als Liste zurück.

        :param directory_path: Pfad des Verzeichnisses, das durchsucht werden soll.
        :param suffix: Das Suffix (z.B. '.txt'), nach dem gefiltert werden soll.
        :return: Liste der Dateinamen mit dem angegebenen Suffix.
        """
        try:
            # Liste zur Speicherung der Dateinamen
            files_list = []
            if directory_path is None:
                directory_path = self._template_path
            # Überprüfung, ob der angegebene Pfad ein Verzeichnis ist
            if not os.path.isdir(directory_path):
                print(f"Der angegebene Pfad '{directory_path}' ist kein Verzeichnis.")
                return files_list

            # Durchsuchen des Verzeichnisses nach Dateien mit dem angegebenen Suffix
            for filename in os.listdir(directory_path):
                if filename.endswith(suffix):
                    if appendPath:
                        filename = os.path.join(directory_path, filename)
                    files_list.append(filename)

            return files_list
        except Exception as e:
            print(f"Fehler beim Lesen der Dateien: {e}")
            return []

def read_number():
    while True:
        try:
            number = input("Wieviel Prompts sollen generiert werden?:")
            number = int(number)
            return number
        except ValueError:
            print("Bitte eine gültige Zahl eingeben")

# Beispiel
template_path = 'genai_training_data/simql_templates'
template_suffix = '.txt'
nlp_path = 'genai_training_data/nlp_data'
nlp_file = 'simql_prompts.txt'
nlp_phrases_file = 'phrase_mappings.json'
nlp_file = os.path.join(nlp_path, nlp_file)
nlp_phrases_file = os.path.join(nlp_path, nlp_phrases_file)
out_path = 'genai_training_data/'

generator = TrainDataGenerator(template_path, nlp_file, nlp_phrases_file, out_path, convertToAbsolutePath=True)
flist = generator.get_template_files_with_suffix()
print(f"TemplateFiles: {flist}")

prompts = generator.load_nlp_data()
print(f"Prompts: {prompts}")

templates = generator.load_templates()
#print(templates)

rows = read_number()
print ("Die exakte Anzahl der generierte Prompts berechnet sich aus {row} / <AnzahlPrompts> + Phrasen")
generator.generate_train_data(rows) 

