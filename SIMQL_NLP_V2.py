import argparse

from textx import metamodel_from_file

# Hugging Face for model, tokenizer, and a training function:
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from transformers import get_linear_schedule_with_warmup
from datasets import Dataset
from modules.ConvertPromptToJson import ConvertPromptToJSON

from torch.utils.data import DataLoader
import torch
import json
import os
import sys


class SIMQL_NLP:
    """ 
    SIMQL_NLP ist eine Klasse die versucht PROMPTs in eine DSL-Sprache (SIMQL) zu übersetzen. Hierzu nutzt
    sie ein vorab trainiertes Modell und parste das PROMPT und wandelt in Source-Code um.
    Der SourceCode wird asl {mmp_alias}.simql File im Verzeichnis 'genai_out' gespeichert.
 
    Details zur Beschreibung siehe README.md

    Zum Trainieren und erstellen des Modells siehe SIMQL_Train.py

    """

    tokinizer = None
    model = None 
    device = None
    mm = None           # DSL Model
    def __init__(self, args):
        self.path_train_data = args.path_train_data
        self.path_model_out = args.path_model_out
        self.path_model = args.path_model
        self.nlp_param_file = args.nlp_param_file
        self.simql_model_path = args.simql_model_path
        self.simql_model_file = args.simql_model_file
        self.translate_prompt_file = args.translate_prompt_file
        self.verbose = args.v
        self.updateModel = args.updateModel
        self.simql_model = None

        pass

    @property
    def tokenizer(self):
        """ return T5-Tokenizer """
        return self._tokenizer
    
    @property
    def model(self):
        """ return T5-Model """
        return self._model
    
    @property
    def device(self):
        """ return device"""
        return self._device
    
    @property 
    def translatePromptJson(self):
        """ return translated user-prompt als JSON """
        return self._translate_prompt
    
    def init(self):
        """ 
        Initialiiserungsprozess und Vorbereitung zur Code-Generierung

        :return True/False - wenn True, dann kann die Generierung durchgeführt werden
        """
        try:
            print(f"Starte Initialisierungsprozess...")
            self.nlp_params = self._load_nlp_parameter_file(self.nlp_param_file)
            print(f"\tNLP-Parameter Datei geladen...")

            self.simql_model_file = os.path.join(self.simql_model_path, self.simql_model_file)
            self.simql_model = self._load_dsl_textx_model(self.simql_model_file)
            print(f"\tSIMQL-Model geladen...")

            self._device, self._model, self._tokenizer = self._init_nlp_model()
            print(f"\tNLP-Modell initialisiert...")

            self._translate_prompt = self._load_translate_prompt_file(self.translate_prompt_file)
            print(f"Zu übersetzendes PROMPT geladen...")


        except Exception as e:
            print(f"Initialisierung fehltgeschlagen")
            return False
        
        return True

    def _load_translate_prompt_file(self, translate_file:str) -> list:
        """
        Lädt eine Datei die den Inhalt dens Prompts und einen Suffix für den zu generierten SIMQL-Datei ein.

        Die Datei kann mehrere PROMPTs enthalten, die sich über mehrere Zeilen erstreckt. Ein Prompt wird grundsätzlich
        mit dem PIPE | Zeichen abgeschlossen.
        Das PROMPT hat den gleichen Aufbau wie Trainingsprompts. Im key 'code' wird der SUFFIX für die zu speicherende
        Datei hinterlegt

        [
            {'prompt':prompt_text, 'template':immer leer, 'code':suffix}, ...
        ]

        :param translate_file Name der TRANSLATE_PROMPT Datei. 
        :return Array of JSON-Dict
        """
        converter = ConvertPromptToJSON('')
        prompt_json = converter.load_and_convert(None, translate_file, False)

        return prompt_json

    def _load_nlp_parameter_file(self, nlp_param_file):
        """
        Lädt die angegebene Parameter-Datei und stellt sie als JSON
        File zur Verfügung. Im Dateinamen kann ein Pfad angegeben werden. In der 
        Regel liegt die Datei im Root-Verzeichnis

        :param nlp_param_file Name der Parameter-Datei
        :return JSON
        """

        # Lesen der Parameter aus der JSON-Datei
        try:
            with open(nlp_param_file, 'r') as f:
                params = json.load(f)
        except FileNotFoundError as e:
            print(f"{nlp_param_file} nicht gefunden. Bitte Parameter --nlp_param_file prüfen")
            raise FileNotFoundError(e)
        except Exception as e:
            print(f"Fehler beim Lesen der Parameterdatei: {e}")
            raise Exception(e)

        return params
    
    def validate_dsl(self, dsl_metamodel, dsl_code):
        try:
            # Validierung des generierten DSL-Codes mit der DSL-Definition
            dsl_metamodel.model_from_str(dsl_code)
            print("DSL-Code ist gültig")
        except Exception as e:
            print(f"ungültiger DSL-Code '{dsl_code}'. Error: '{e}'")

    def _load_dsl_textx_model(self, dsl_file_path):
        try:
            self.mm = metamodel_from_file(dsl_file_path)
            return self.mm
        except Exception as e:
            print(f"Fehler beim Laden der DSL-Definition: {e}")
            return None

    def _init_nlp_model(self):
        """ 
        Erzeugt ein T5ForConditionalGeneration NLP-Modell

        device:     Wie (gerät) soll das NLP-Modell arbeiten (CPU, MPS(osx), )
        model:      T5-Modell basierend auf das vortrainierte Modell
        tokenizer:  erstellte Tokens basierend auf Trainingsdaten

        self._tokenizer
        diese Tokens werden später für eine Umwandlung von PROMPT zu Code genutzt um Übereinstimmungen
        zu nutzen und Verweise auf Code zu nutzen

        self._model
        das eigentlich T5-Modell basierend auf ein vor-trainiertes Modell

        :return device Rückgabe einens Torch-Devices
        :return model Rückgabe des generierte T5-Models
        :return tokenizer Rückgabe einen T5-Tokenizers
        """
        try:
            # Festlegen des Geräts auf 'mps', falls verfügbar
            self._device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

            # gibt es ein Finetuning-Modell? wenn nein, nutze ein default_pretrained model
            if len(os.listdir(self.path_model)) == 0:
                self.path_model=None

            # Verwende das T5 Modell für Text-zu-Text Generierung
            if self.path_model is None:
                self._tokenizer = T5Tokenizer.from_pretrained('t5-base')
                self._model = T5ForConditionalGeneration.from_pretrained('t5-base').to(self._device)
                print("Default NLP Modell erfolgreich initialisiert.")
            else:
                self._tokenizer = T5Tokenizer.from_pretrained(self.path_model)
                self._model = T5ForConditionalGeneration.from_pretrained(self.path_model).to(self._device)
                self._model.resize_token_embeddings(len(self._tokenizer))

                print("SIMQL NLP Modell erfolgreich initialisiert.")

            print(f"Anzahl geladener Tokens: {len(self._tokenizer)}")

            return self._device, self._model, self._tokenizer
        except Exception as e:
            print(f"Fehler bei der Initialisierung des NLP Modells: {e}")
            return None, None, None

    def generate_dsl_code(self, device, model, tokenizer, user_inputs, save_output:bool=True):
        try:

            for prompt in user_inputs:
                file_name_part = prompt['code']
                prompt = prompt['prompt']
                input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
                print(f"Translate prompt:\n'{prompt}'")
                outputs = model.generate(
                    input_ids, 
                    max_length=self.nlp_params['tokenizer_max_length'],
                    num_beams=self.nlp_params['num_beams'],                 # Anzahl der Beams für Beam Search
                    early_stopping=True,                                    # Frühzeitiger Stopp, wenn die Ausgabe vollständig 
                    no_repeat_ngram_size=self.nlp_params['ngram_size'],     # Vermeidet Wiederholungen von N-Grammen
                    temperature=self.nlp_params['temperature'],             # Steuerung der Kreativität der Ausgabe
                    top_k=self.nlp_params['top_k'],                         # Begrenzung auf die 50 wahrscheinlichsten Token
                    top_p=self.nlp_params['top_p'],                         # Nutze die Top 95% der kumulierten Wahrscheinlichkeiten
                    do_sample=True
                    )
                dsl_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"\ngenerierter DSL-Code:\n{dsl_code}")
                if save_output:
                    file_name = f"simql_{file_name_part}.simql"
                    file_name = os.path.join(self.path_model_out, file_name)
                    self._save_simql_code_to_file(file_name=file_name, data=dsl_code)
                    print(f"DSL File erstellt. '{file_name}")
                return dsl_code
        except Exception as e:
            print(f"Fehler bei der Generierung des DSL-Codes: {e}")
            return ""

    def _save_simql_code_to_file(self, file_name:str, data:str):
        """ 
        Speichert eine generierte SIMQL-Datei mit dem Namen file_name im Verzeichnis self.path_model_out

        :param file_name Ausgabe-Dateiname.
        :param data SIMQL-Code
        """
        with open(file_name, 'w') as dsl:
            dsl.writelines(data)
            dsl.close
        pass

    # # Hilfsfunktion zum Tokenisieren der Daten
    # def preprocess_function(self,examples):
    #     #inputs = [ex["text"] for ex in examples]
    #     inputs = examples["text"]
    #     #targets = [ex["code"] for ex in examples]
    #     targets = examples["code"]
    #     model_inputs = tokenizer(
    #         inputs, 
    #         max_length=tokenizer_max_length, 
    #         truncation=True, 
    #         padding="max_length")

    #     # Tokenisierung der Labels
    #     with tokenizer.as_target_tokenizer():
    #         labels = tokenizer(
    #             targets, 
    #             max_length=tokenizer_max_length, 
    #             truncation=True, 
    #             padding="max_length")

    #     model_inputs["labels"] = labels["input_ids"]
    #     return model_inputs




def parse_arguments():
    """
    Parsed die Kommandozeilenargumente und gibt sie zurück.
    """
    parser = argparse.ArgumentParser(description="SIMQL NLP V2")
    parser.add_argument('--path_train_data', required=True, help='Pfad zu den Trainingsdaten')
    parser.add_argument('--path_model_out', required=True, help='Pfad zu generierten SIMQL-Dateien')
    parser.add_argument('--path_model', required=True, help='Pfad zum trainierten NLP-Modell')
    parser.add_argument('--nlp_param_file', required=True, help="JSON File für NLP-Parameter")
    parser.add_argument('--simql_model_path', required=True, help='Pfad zur SIMQL .tx Modell Datei')
    parser.add_argument('--simql_model_file', required=True, help='SIMQL .tx Modell Datei')
    parser.add_argument('--translate_prompt_file', required=True, help="PROMPT-File.txt das in Source-Code umgewandelt werden soll")
    parser.add_argument('-u', "--updateModel", default=True, action='store_true', help='Wenn gesetzt (default), wird das aktuelle Modell erweitert')
    parser.add_argument('-v', action='count', help='Verbosity, -v, -vv, -vvv')
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    prompt = ""

    try:
        nlp = SIMQL_NLP(args)
        initialized = nlp.init()
        if initialized:
            print("Starte SIMQL-Generierung...")
            dsl_code = nlp.generate_dsl_code(device=nlp.device, model=nlp.model, tokenizer=nlp.tokenizer, user_inputs=nlp.translatePromptJson)
            pass
        

    except ValueError as ve:
        print(f"Fehler: {ve}")
        sys.exit(1)

if __name__ == "__main__":
    main()
