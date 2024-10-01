# Hugging Face for model, tokenizer, and a training function:
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import get_linear_schedule_with_warmup
from datasets import Dataset
from modules.LoadTrainData import LoadTrainData
from prettytable import PrettyTable
from modules.CodeTimer import CodeTimer
from modules.utils import *
from collections import Counter

from torch.utils.data import DataLoader
import torch.multiprocessing as mp

import torch
import argparse
import pandas as pd
import sys
import os
import json
import multiprocessing

class SIMQL_NLP_Training:
    def __init__(self, args):
        self.path_train_data = args.path_train_data     # Pfad zu den Trainingsdaten
        self.output_dir = args.output_dir               # Pfad zum NLP-Model Verzeichnis
        self.nlp_param_file = args.nlp_param_file       # Parameter Datei zur Konfiguration des Models
        self.resetModel = args.resetModel               # True: löscht aktuelles Model und startet mit Default model, False: updated das aktuelle Model
        self.train_files = args.train_files             # liste an Training-Files
        self.verbose = args.v
        self.train_model = args.train_model                    # Angabe des Default Models was zum Vortrainieren genutzt wird
        self.tokens_file = args.tokens_file             # tokens.txt File 
        self.nlp_params = self._load_nlp_parameter_file(self.nlp_param_file)
        self.type_tokenizer = args.tokenizer            # Auswahl des Tokenizers (T5Tokenizer oder AutoTokenizer)

        #--------------------------------------------------------------------------------------------------------------------------------------------------
        # Anmerkungen zu den T5-Modellen
        # T5-small, ca 60Mio Parameter, kleines Modell, wenig Rechenkapazität
        # T5-base, ca 220Mio Parameter, gute Balance zwischen Rechenaufwand und Genauigkeit
        # T5-large, ca 770Mio Parameter, Bietet eine bessere Leistung als T5-BASE, aber mit höherem Rechenaufwand
        # T5-3B, 3 Millarden Paramete, sehr groß, Bietet eine hohe Genauigkeit und ist für Aufgaben gedacht, die sehr leistungsstarke Modelle erfordern
        # T5-11B, das größte T5-Modell, 11 Millarden, Sehr präzise und leistungsstark
        #--------------------------------------------------------------------------------------------------------------------------------------------------



        if self.resetModel == True:
            print(f"****************************************************************")
            print(f"* Ein bestehendes Modell wird zurückgesetzt und neu aufgebaut. *")
            print(f"****************************************************************")
            v = input("Soll das wirklich durchgeführt werden? Bestätige mit YES/JA (beliebige Taste für Abbruch): ").strip().lower()
            if v not in ['yes', 'ja']:
                print("Training abgebrochen. Bitte den Aufrufparameter --resetModel ggf. entfernen")
                sys.exit(1)

    def init(self) -> bool:
        # Vorbereitenungen 
        #timer = CodeTimer("Initialisierung")
        self._init_nlp_model()
        self.df_train = self._load_train_data_files()
        self._calculate_token_count(self.df_train)

        #self.tbl_timer.add_row(['init', timer.stop()])
        if self.df_train.shape[0] > 0:
            return True        
        print(f"Fehler bei der Initialisierung")
        return False
        

    def _calculate_token_count(self, df):
        token_counts = Counter()
        all_data = []
        #
        # lese alle prompts aus der Text-Spalte und konvertiere sie in eine Liste
        for c in df.columns:
            li = df[c].to_list()
            all_data.append(li)


        for text in all_data:
            for t in text:
                tokens = self.tokenizer.tokenize(t)
                token_counts.update(tokens)

        for token, count in token_counts.items():
            print(f"Token: {token}, Häufigkeit: {count}")



    def _load_train_data_files(self, loadType='json') -> pd.DataFrame:
        """ 
        Iteriert alle files aus self.train_files und lädt jedes Traingingsfiel in ein
        Pandas-Dataframe.

        """
        self.loader = LoadTrainData(
            path=self.path_train_data,
            loadType='json'
        )
        df_combined = pd.DataFrame()

        for file in self.train_files:
            file = eval(file)   # zusätzliche "" entfernen. Die entstehen durch die Parameter-Übergabe
            print(f"Load Trainings-File '{file}'")
            df_tmp = self.loader.load(file)
            df_combined = pd.concat([df_combined, df_tmp], axis=0, sort=False, ignore_index=True)

        print(f"Combinded dataset size: {df_combined.shape}")
        return df_combined

    def torch_worker(self, rank, threads=1):
        torch.set_num_threads(threads)
        print (f"Prozess {rank} läuft auf {self.device} mit {threads} Threads.")

    def _init_nlp_model(self):
        """ 
        Initialisierz ein T5-NLP Modell

        :return device
        :return model Gibt das initialsierte T5-Modell zurück, bereit zum lernen
        :return tokenizer Gibt ein Tokenizer-Objekt zurück
        """
        try:
            self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

            #
            # unter MacOS ist es besser (effizienter) mit 'mps' (MetalPerformanceShader) zu arbeiten als mit 'cpu'
            if self.nlp_params['device'] == 'cpu' or self.device == 'cpu':
                if self.nlp_params['system'] == 'osx-m3':
                    multiprocessing.set_start_method('fork', force=True)
                print (f"Modell wird auf CPU-Basis aufgesetzt ...")
                self.device = torch.device("cpu")
                tensor = torch.randn(1, 10).to(self.device)
                print(f"Tensor: {tensor}")
                mp.spawn(
                    self.torch_worker, 
                    args=(self.nlp_params['torch_threads'],), 
                    nprocs=self.nlp_params['dataloader_num_workers'], 
                    join=True)

            if self.resetModel:
#                self.tokenizer = T5Tokenizer.from_pretrained(self.t5_model)
                if self.type_tokenizer == 'T5':
                    self.tokenizer = T5Tokenizer.from_pretrained(self.train_model)
                elif self.type_tokenizer == 'auto':
                    self.tokenizer = AutoTokenizer.from_pretrained(self.train_model)

                self.model = T5ForConditionalGeneration.from_pretrained(self.train_model).to(self.device)
                print(f"Default Pre-Trained model : '{self.train_model}'")
            else:
                if self.type_tokenizer == 'T5':
                    self.tokenizer = T5Tokenizer.from_pretrained(self.output_dir)
                elif self.type_tokenizer == 'auto':
                    self.tokenizer = AutoTokenizer.from_pretrained(self.output_dir)

#                self.tokenizer = self.usedTokenizer.from_pretrained(self.output_dir)
                self.model = T5ForConditionalGeneration.from_pretrained(self.output_dir).to(self.device)
                print(f"SIMQL NLP Modell erfolgreich geladen.")

            print(f"Anzahl geladener Tokens: {len(self.tokenizer)}")

            print(f"Device : {self.model.device}")
        except Exception as e:
            print(f"Fehler bei der Initialisierung des NLP Models: '{e}'")
            raise Exception(e)
        
        return self.device, self.model, self.tokenizer

    def _load_dsl_tokens(self, path:str, file_name='tokens.txt'):
        file_name = os.path.join(path, file_name)
        with open(file_name,'r') as file:
            tokens = [line.strip() for line in file]

        #print (f"DSL-Tokens: {tokens}")
        return tokens



#    def tuning_model(self, device, model, tokenizer, train_file_path, output_dir, update:True):
    def tuning_model(self):
        """ 
            Tuned das aktuelle Modell auf basis der als Parameter übegebenen Traingingsdaten

        # :param device       Device
        # :param model        T5-Model-Objekt
        # :param tokenizer    Tokenizer-Objekt
        # :train_file_path    Verzeichnis wo die Trainingsdaten liegen
        # :output_dir         Verzeichnis des trainierten Modells
        # :update_model       bool, Default True : update eines bestehenden Models, False: reset und neues modell
        """
        print(f"Start training....")
        trained_data_json = self.loader.getJson(self.df_train)
        print(f"Geladene Trainingsätze: {len(trained_data_json)}")

        additional_tokens =  set()
        #
        # Prompts als Tokens aufnehmen
        # SIMQL-Code als Tokens aufnehmen
        for text in trained_data_json:
            words = text['text'].split()
            codes = text['code'].split()
            additional_tokens.update(words)
            additional_tokens.update(codes)

        additional_tokens = sorted(list(remove_entries_by_pattern(
            additional_tokens, 
            wildcard_patterns=["AUTO*","MMP*_*",".", "#", "#all", "#save"],
            regex_patterns=[r"\"MMP\d+_.+\"", r"\'MMP\d+_.+\'"]  
        )))
        additional_tokens = sorted(list(remove_entries_by_pattern(
            additional_tokens, 
            regex_patterns=[r"\"", r"\'"]  
        )))
        # save_text_file('./', 'additional_tokens.txt', all_tokens)


        dataset = Dataset.from_list(trained_data_json)

        model_eval = {}

        self.tbl_timer = PrettyTable()
        self.tbl_timer.field_names = ['Part','Timing in secs']
        self.tbl_timer.align['Part'] = 'l'
        self.tbl_timer.align['Timing in secs'] = 'l'
        self.tbl_timer.add_row(['Datalaoder workers', self.nlp_params['dataloader_num_workers']])

        #
        # Spezielle Tokens zuerst dem Tokenizer übergeben
        #
        dsl_tokens = self._load_dsl_tokens('./',self.tokens_file)
        self.tokenizer.add_tokens(dsl_tokens)
        self.tokenizer.add_tokens(additional_tokens)

        # Anpassen des Modells an die neue Größe des Tokenizers
        self.model.resize_token_embeddings(len(self.tokenizer))
        print(f"Nachladen spezieller Tokens. Neue Tokenizer-Größe: {len(self.tokenizer)}")


        #
        # Trainingsdaten werden gesplittet in der Form das es 
        # x% Trainingsdaten gibt mit den das Modell trainiert wird
        # y% der Daten sind dem modell unbekannt und hiermit wird das Modell pre-testet
        #
        # Beispiel:
        # self.nlp_params['split_size'] = 0.25 
        #   75% für Trainingsdaten, 25% für unbekannte Daten zur Evaluierung
        #
        train_test_split = dataset.train_test_split(test_size=self.nlp_params['split_size'])
        train_dataset = train_test_split['train']
        eval_dataset = train_test_split['test']

        train_dataset = train_dataset.map(self.preprocess_function, batched=True)
        eval_dataset = eval_dataset.map(self.preprocess_function, batched=True)

        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)
        tbl = PrettyTable()

        tbl.field_names = ['Training', 'Evaluate']
        tbl.align['Training'] = 'l'
        tbl.align['Evaluate'] = 'l'
        
        # Definiere die Trainingsparameter
        learning_rates = self.nlp_params['learning_rates'][self.nlp_params['learning_rate_idx']]

        training_args = TrainingArguments(
            eval_strategy="epoch",
            learning_rate=learning_rates,
            fp16=self.nlp_params['fp16'],
            weight_decay=self.nlp_params['weight_decay'],
            num_train_epochs=self.nlp_params['epochs'],
            per_device_train_batch_size=self.nlp_params['batch_size'],
            per_device_eval_batch_size=self.nlp_params['eval_batch_size'],
            save_steps=10_000,
            save_total_limit=2,
            output_dir=self.output_dir,
            dataloader_num_workers=self.nlp_params['dataloader_num_workers'],

            logging_dir='./logs',
        
        )

        trainer = Trainer(
            model = self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )

        training = 'pre_train'

        print(f"Pre-Trained Evaluierung (kann mehrere Minuten dauern).....")

        with CodeTimer("PRE-Trained Model Evaluierung - TIMER") as timer:
            model_eval[training] = trainer.evaluate()

        self.tbl_timer.add_row(['Pre-Evaluierung', timer.stop()])
        tbl.add_row(['pre-trained', json.dumps(model_eval[training],indent=4)])
        print(f"Pre-Train :\n{ model_eval[training]} ")

        #------------------------------------------------------------------------------------------------
        # ACHTUNG wenn man Verbose auf 2 oder größer setzt verlangsamt sich das Training enorm, es 
        # werden aber aus dem eval_dataset für jeden einzelnen Datensatz ein Output generiert.
        # zum Debuggen/Üben/Monitoren hilfreich - aber LANGSAM
        #
        #------------------------------------------------------------------------------------------------
        max_length = self.nlp_params['tokenizer_max_length']
        if self.verbose > 1:
            i=0
            for example in eval_dataset:
                print(f"{i:4d} erstelle Output für Evaluierungsdatensatz...")
                input_text = example['text']
                input_ids = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)
                outputs = self.model.generate(
                    input_ids,
                    max_length = max_length,
                    num_beams = self.nlp_params['num_beams'],
                    early_stopping = True,
                    no_repeat_ngram_size=2,
                    do_sample=True
                )
            dsl_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Eingabetext: {input_text}")
            print(f"Erwarteter DSL-Code: \n{example['code']}")
            print(f"Generierter DSL-Code: {dsl_code}")                
        #-END-------------------------------------------------------------------------------------------
        with CodeTimer("START Training - TIMER") as timer:
            trainer.train()
        self.tbl_timer.add_row(['Training', timer.stop()])

        training = 'post_train'
        with CodeTimer("POST-Trained Model Evaluierung - TIMER") as timer:
            model_eval[training] = trainer.evaluate()

        self.tbl_timer.add_row(['POST-Evaluierung', timer.stop()])
        tbl.add_row(['post-trained', json.dumps(model_eval[training], indent=4)])     
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        print(f"\nModell erfolgreich feingetunt und gespeichert in: {self.output_dir}")
        print(tbl)   
        print(self.tbl_timer)
        


    # Hilfsfunktion zum Tokenisieren der Daten
    def preprocess_function(self, examples):
        #inputs = [ex["text"] for ex in examples]
        inputs = examples["text"]
        #targets = [ex["code"] for ex in examples]
        dsl_output = examples["code"]
        max_length = self.nlp_params['tokenizer_max_length']
        model_inputs = self.tokenizer(
            inputs, 
            max_length=max_length, 
            truncation=True, 
            padding="max_length")

        # Tokenisierung der Labels
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(
                dsl_output, 
                max_length=max_length, 
                truncation=True, 
                padding="max_length")

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs



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


#----------------------------------------------------------------------------------------------------
# Aufruf der SIMQL-Training Klasse
# 
#----------------------------------------------------------------------------------------------------
def parse_arguments():
    """
    Parsed die Kommandozeilenargumente und gibt sie zurück.
    """
    parser = argparse.ArgumentParser(description="SIMQL NLP V2")
    parser.add_argument('--path_train_data', required=True, help='Pfad zu den Trainingsdaten')
    parser.add_argument('--output_dir', required=True, help='Pfad zum gespeicherten trainierten NLP-Modell')
    parser.add_argument('--train_files', required=True, type=lambda s: s.strip("[]").split(','), help="Liste von Dateinamen im Format ['file1', 'file2', 'file3']")
    parser.add_argument('--nlp_param_file', required=True, help="JSON File für NLP-Parameter")
    parser.add_argument('--train_model', default='T5-small', help="Verwendung dieses Default-Training-Models. T5-small, T5-base, T5-large, T5-3B, T5-11b")
    parser.add_argument('--tokens_file', default='tokens.txt', help="Spezielle DSL-Tokens")
    parser.add_argument('--tokenizer', default='auto', help="Auswahl eines Tokenizers (T5Tokenizer = t5 oder AutoTokenizer = auto)")
    parser.add_argument('-r', "--resetModel", default=False, action='store_true', help='wenn True, wird das aktuelle Modell zurückgesetzt, (Default)=False, aktuelles Modell wird erweitert')
    parser.add_argument('-v', action='count', help='Verbosity, -v, -vv, -vvv')
    return parser.parse_args()


def main():

    # vermeidedit die huggingface/tokenizer warnung: huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
    os.environ['TOKENIZERS_PARALLELISM'] = 'true'
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = str(1)

    args = parse_arguments()
    
    prompt = ""

    try:
        nlp = SIMQL_NLP_Training(args)
        initialized = nlp.init()
        if initialized:
            print("Starte SIMQL-Training...")
            print("Dieser Vorgang kanne je nach Umfang der Trainingsdaten und der Modell-Einstellungen mehrere Stunden dauern...")
            nlp.tuning_model()
            
        

    except ValueError as e:
        print(f"ValueError: {e}")
        sys.exit(1)
    #except Exception as e:
    #    print(f"Unbekannter Fehler: Error '{e}'")

if __name__ == "__main__":
    main()