import pandas as pd
import re
from pathlib import Path
import os
from numbers_parser import Document

class LoadTrainData:
    def __init__(self, path:str, input_file:str=None, sep:str='#', loadType:str='json'):
        self.sep = sep
        self.path = path 
        self.loadType = loadType

        self.input_file = input_file 
        if input_file is None:
            self.input_file = 'DEFAULT_INPUT_FILE.json'
        self.output_file = Path(self.input_file).stem + '.json'
        self.output_file = os.path.join(self.path, self.output_file)
        self.input_file = os.path.join(self.path, self.input_file)

    @property
    def output_path_file(self) -> str:
        """ gibt den Pfad und Dateinamen der Trainingsdatensatzes zurück """
        return self.output_file

    def load(self, input_file=None) -> pd.DataFrame:
        """
        Lese Trainingsdaten in ein Dataframe und gebe dieses zurück
        
        :param input_file Default None, wenn angegeben wird diese Datei gelesen und self.input_file überschrieben, ansonsten self.input_file
        """
        try:
            if input_file is not None:
                self.input_file = os.path.join(self.path, input_file)
            if self.loadType == "numbers":
                print("Load trainingsdaten aus Mac-Numbers file")
                self._df = self.__load_numbers()
            elif self.loadType == "csv":
                print("Load trainingsdaten aus CSV-File")
                self._df = pd.read_csv(self.input_file, sep=self.sep)
            elif self.loadType == 'json':
                print("Load trainingsdaten aus JSON-File")
                self._df = pd.read_json(self.input_file, orient='records')
            else:
                print("unbekannte Dateityp")
                raise IOError("wrong load type")
        except FileNotFoundError as e:
            print(f"Trainingsfile '{file}' not found. Error {e}")
            raise Exception(e)
    
        print(f"Trainingsdaten gelesen: {self._df.shape}")
        return self._df
    
    def getJson(self, df: pd.DataFrame=None):
        """ konvertiert dataframe in eine JSON-Struktur"""
        if df is None:
            df = self._df    
        out=df.to_dict(orient='records')

        print(f"JSON Struct len({len(out)})")
        return out

    def __load_numbers(self) -> pd.DataFrame:
        """ lädt eine Mac-Numbers Datei und gibt ein Pandas Dataframe zurück"""
        doc = Document(self.input_file)
        for sheet in doc.sheets:
            for table in sheet.tables:
                data = table.rows(values_only=True)
                df = pd.DataFrame(data[1:], columns=data[0])
        df.dropna(inplace=True)
        return df
    
    def __loadJSONFile(self) -> pd.DataFrame:
        """
        Lädt den Inhalt der JSON-Datei und gibt ihn als Liste von Dictionaries zurück.
        
        :return: Liste von Dictionaries, die in der JSON-Datei gespeichert sind.
        """
        with open(json_file, 'r') as file:
            data = json.load(file)
        df = pd.DataFrame(data)
        return df

# Nutzung der Klasse
# train_path = "genai_training_data/simql_data"
# train_file = "dsl_examples_10000.json"

# #converter = TextToJsonConverter('genai_training_data/train_simql_computedata2.txt', 'genai_training_data/train_simql_computedata1.json')
# converter = LoadTrainData(train_path, train_file, loadType='json')
# converter.load()
# data = converter.getJson()
