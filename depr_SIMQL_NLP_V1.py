# Installiere die notwendigen Bibliotheken
# pip install textx transformers torch pandas

import argparse

from textx import metamodel_from_file

# Hugging Face for model, tokenizer, and a training function:
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from transformers import get_linear_schedule_with_warmup
from datasets import Dataset

from torch.utils.data import DataLoader
import torch
import json
import os
#from modules.TextToJsonConverter import TextToJsonConverter
from modules.LoadTrainData import LoadTrainData

# Nutzung der Klasse
train_path = "genai_training_data/"
train_file = "simql_prompts_000533.json"

print("---------------------------------------------------------------------")
train_data = input("Gebe den Trainingsdaten-Dateinamen ein:")
if len(train_data) > 0:
    train_file = train_data

converter = LoadTrainData(train_path, train_file, loadType='json')
df_train = converter.load()

#converter = TextToJsonConverter('genai_training_data/train_simql_computedata1.txt', 'genai_training_data/train_simql_computedata1.json')
simql_model_idx = 1
simql_model = [
    "simql_model/model.tx",
    "simql_model/model_compute_data.tx"
]

tokenizer_max_length = 256
nlp_temperature=0.2
nlp_num_beams=3
num_beams=10
ngram_size=2
train_learning_rates=[1e-5, 2e-5, 3e-5, 5e-5]
train_learning_rate_idx = 2
train_epochs = 3
train_batch_size = 8
train_eval_batch_size = 8
split_size = 0.25
top_k = 50
top_p = 0.95

# Festlegen des Geräts auf 'mps', falls verfügbar
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")


# Schritt 1: Laden der DSL-Metadatei
def load_dsl_definition(dsl_file_path):
    try:
        mm = metamodel_from_file(dsl_file_path)
        print("SIMQL-DSL Definition erfolgreich geladen.")
        return mm
    except Exception as e:
        print(f"Fehler beim Laden der DSL-Definition: {e}")
        return None

def validate_dsl(dsl_metamodel, dsl_code):
    try:
        # Validierung des generierten DSL-Codes mit der DSL-Definition
        dsl_metamodel.model_from_str(dsl_code)
        print("DSL-Code ist gültig.")
        return True
    except Exception as e:
        print(f"Ungültiger DSL-Code: {e}")
        return False

# Schritt 2: Initialisieren des NLP-Modells
def init_nlp_model(model_dir= None):
    try:
        # Festlegen des Geräts auf 'mps', falls verfügbar
        device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

        # gibt es ein Finetuning-Modell? wenn nein, nutze ein default_pretrained model
        if len(os.listdir(model_dir)) == 0:
            model_dir=None

        # Verwende das T5 Modell für Text-zu-Text Generierung
        if model_dir is None:
            tokenizer = T5Tokenizer.from_pretrained('t5-base')
            model = T5ForConditionalGeneration.from_pretrained('t5-base').to(device)
            print("Default NLP Modell erfolgreich initialisiert.")
        else:
            tokenizer = T5Tokenizer.from_pretrained(model_dir)
            model = T5ForConditionalGeneration.from_pretrained(model_dir).to(device)
            print("SIMQL NLP Modell erfolgreich initialisiert.")

        return device, model, tokenizer
    except Exception as e:
        print(f"Fehler bei der Initialisierung des NLP Modells: {e}")
        return None, None

# Schritt 3: DSL Code generieren aus natürlicher Sprache
def generate_dsl_code(device, nlp_model, tokenizer, user_input):
    try:
        input_ids = tokenizer.encode(user_input, return_tensors='pt').to(device)
        outputs = nlp_model.generate(
            input_ids, 
            max_length=tokenizer_max_length, 
            num_beams=nlp_num_beams,        # Anzahl der Beams für Beam Search
            early_stopping=True,        # Frühzeitiger Stopp, wenn die Ausgabe vollständig 
            no_repeat_ngram_size=ngram_size,     # Vermeidet Wiederholungen von N-Grammen
            temperature=nlp_temperature,            # Steuerung der Kreativität der Ausgabe
            top_k=top_k,  # Begrenzung auf die 50 wahrscheinlichsten Token
            top_p=top_p,  # Nutze die Top 95% der kumulierten Wahrscheinlichkeiten
            do_sample=True
            )
        dsl_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"DSL Code erfolgreich generiert. '{dsl_code}'")
        return dsl_code
    except Exception as e:
        print(f"Fehler bei der Generierung des DSL-Codes: {e}")
        return ""

# Hilfsfunktion zum Tokenisieren der Daten
def preprocess_function(examples):
    #inputs = [ex["text"] for ex in examples]
    inputs = examples["text"]
    #targets = [ex["code"] for ex in examples]
    targets = examples["code"]
    model_inputs = tokenizer(
        inputs, 
        max_length=tokenizer_max_length, 
        truncation=True, 
        padding="max_length")

    # Tokenisierung der Labels
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets, 
            max_length=tokenizer_max_length, 
            truncation=True, 
            padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


# Schritt 4: Feintuning Funktion
def finetune_model(device, model, tokenizer, train_file_path, output_dir):

    #train_data = converter.load_json_file(train_file_path)
    train_data = converter.getJson()
    dataset = Dataset.from_list(train_data)

    train_test_split = dataset.train_test_split(test_size=split_size)  # 80% Training, 20% Evaluation
    train_dataset = train_test_split['train']
    eval_dataset = train_test_split['test']

    train_dataset = train_dataset.map(preprocess_function, batched=True)
    eval_dataset = eval_dataset.map(preprocess_function, batched=True)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Definiere die Trainingsparameter
    training_args = TrainingArguments(
        eval_strategy="epoch",
        learning_rate=train_learning_rates[train_learning_rate_idx],
        weight_decay=0.01,
        num_train_epochs=train_epochs,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=train_eval_batch_size,
        save_steps=10_000,
        save_total_limit=2,
        output_dir=output_dir,
        logging_dir='./logs',
     
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,  
        data_collator=data_collator,
    )

    # Evaluierung des Modells
    eval_results = trainer.evaluate()

    # Zeige die Ergebnisse der Evaluierung an
    print("Evaluierungsergebnisse:", eval_results)

    # i=0
    # for example in eval_dataset:
    #     print(f"{i} generate output für jeden Evaluierungsdatensatz....")
    #     i=i+1
    #     input_text = example["text"]
    #     input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
    #     outputs = model.generate(
    #         input_ids,
    #         max_length=nlp_max_length,
    #         num_beams=nlp_num_beams,
    #         early_stopping=True,
    #         no_repeat_ngram_size=2,
    #         #temperature=nlp_temperature,
    #         do_sample=True
    # )
    # dsl_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # print(f"Eingabetext: {input_text}")
    # print(f"Erwarteter DSL-Code: \n{example['code']}")
    # print(f"Generierter DSL-Code: {dsl_code}")        

    # Trainiere das Modell
    trainer.train()

    # Speichern des feingetunten Modells
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Modell erfolgreich feingetunt und gespeichert in: {output_dir}")

# # Nutzung der Klasse
# train_path = "genai_training_data/"
# train_file = "simql_prompts_000533.json"

# print("---------------------------------------------------------------------")
# train_data = input("Gebe den Trainingsdaten-Dateinamen ein:")
# if len(train_data) > 0:
#     train_file = train_data

# converter = LoadTrainData(train_path, train_file, loadType='json')
# df_train = converter.load()

# #converter = TextToJsonConverter('genai_training_data/train_simql_computedata1.txt', 'genai_training_data/train_simql_computedata1.json')
# simql_model_idx = 1
# simql_model = [
#     "simql_model/model.tx",
#     "simql_model/model_compute_data.tx"
# ]

# tokenizer_max_length = 256
# nlp_temperature=0.2
# nlp_num_beams=3
# num_beams=10
# ngram_size=2
# train_learning_rates=[1e-5, 2e-5, 3e-5, 5e-5]
# train_learning_rate_idx = 2
# train_epochs = 3
# train_batch_size = 8
# train_eval_batch_size = 8
# split_size = 0.25
# top_k = 50
# top_p = 0.95


# Hauptprogramm
if __name__ == "__main__":

    args = parse_arguments()


    # Pfad zur DSL-Metadatei (z.B. dsl.tx)
    dsl_file_path = simql_model[simql_model_idx]

    # Lade die DSL Definition
    print(f"Lade SIMQL-Model '{dsl_file_path}")
    dsl_metamodel = load_dsl_definition(dsl_file_path)

    if dsl_metamodel:
        # Initialisiere das NLP Modell
        device, model, tokenizer = init_nlp_model('./genai_model')
        #model, tokenizer = init_nlp_model()

        if model and tokenizer:
            # Wahl zwischen Modellnutzung und Feintuning
            mode = input("Möchten Sie (1) DSL Code generieren oder (2) das Modell feintunen? (1/2): ")

            if mode == "1":
                # Eingabe des Benutzers
                user_input = input("Bitte geben Sie Ihren Text ein: ")

                # Generiere den DSL-Code
                dsl_code = generate_dsl_code(device, model, tokenizer, user_input)

                # Zeige den generierten DSL-Code an
                if validate_dsl(dsl_metamodel=dsl_metamodel, dsl_code=dsl_code):
                    print("Der generierte DSL-Code ist korrekt und entspricht der DSL-Definition.")
                else:
                    print("Der generierte DSL-Code ist fehlerhaft und entspricht nicht der DSL-Definition.")                

            elif mode == "2":
                # Pfad zur Datei mit Trainingsdaten
                train_file_path = "/Users/bernhardklein/workspace/python/SIMQLGenAI/genai_training_data/train_simql_computedata1.json"
                output_dir = "/Users/bernhardklein/workspace/python/SIMQLGenAI/genai_model/"

                # Feintune das Modell mit den hochgeladenen Daten
                finetune_model(device, model, tokenizer, train_file_path, output_dir)
