# SIMQL-Training

Notwendige Parameter zum Trainieren werden in einer separaten simql_nlp_params.json Datei definiert und zum Trainingsstart geladen. Dieses Verfahren ist deutlich einfacher als hard-coden oder alles über argparse-parameter zu definieren



# PROMPTs erfassen
Prompts können entweder tatsächlich als Datei erfasst werden (Notwendig bei komplexen Prompt-Zusammenhängen) oder man nutzt den SIMQL_prompt_generator.py. Dieses Modul nutzt eine JSON-Augmentation Datei und generiert aus dieser Datei beliebig viele Prompts. Allerdings sind diese prompts in ihrer Komplexität begrenzt

## Manuelle Prompts erstellen
Um Trainieren zu können, müssen im ersten Schritte PROMPTs erfasst werden und den dazugehörigen SIMQL-Code. Die Erfassung dieser Daten wird in einer TXT Datei durchgeführt umd der Aufbau ist wie folgt

```
prompt: Generiere einen MMP {mmp_alias} und dem Businesskey {mmp_name}:
template:
code: mmp {mmp_alias}\n\tregister "{mmp_name}"\n\nend
|
```

Der Aufbau von 'code:' kann von Einfach bis komplex sein. Komplexe Strukturen sollten in einem Template hinterlegt werden und der Template-Name (Dateiname ohne Suffix) im Bereich 'template' eingetragen werden

## Prompt-Generator (Augmentation)

## Vorgehensweise
- **Erfassen der PROMPT-Datei(en)** und speicheren unter 'genai_training/prompts'. Dateinamen müssen mit 'prompt_<freierText>.txt' gespeichert werden
- **Umwandlung der PROMPT-Daten** in ladefähige JSON-Files über 'TrainDataGeneratorV2.py'. In diesem Step werden nun die variablen Inhalte {xxx} mit Random-Werte befüllt. Durch den Parameter --num_records wird die Anzahl der zu generierenden Datensätze angegeben.
- **Trainingsdaten erzeugen** durch die Klasse 'SIMQL_NLP_Train_V1.py' laden.
**Beispiel:** Im Beispiel werden 500 Datensätze generiert und wenn im `prompts` Verzeichnis mehrere Dateien liegen, werden alle gelesen `--read_all`.
```
TrainDataGeneratorV2.py -v -n 500 --path_prompt genai_training/prompts --path_template genai_training/simql_templates --out_path genai_training/out_data --read_all
```

- **Trainings-Modell erstellen:** - dies wird über das Programm `SIMQL_NLP_Train_V1.py` durchgeführt. In diesem Schritt werden die vorbereiteten Prompts inkl. des korrespondierenden SIMQL-Codes geladen und ein T5-Modell generiert. Über den Parameter `--resetModel` kann ein bestehendes Modell komplett zurückgesetzt werden und ein Basis-PreTrained Modell verwedent werden. Welches Basis-Modell verwendet werden soll, wird über den parameter `--T5Model` angegeben. Default ist `t5-small`. Je nach größe der Trainingsdaten und Basis-Model kann ein Training mehrere Stunden dauern.
Wird der Parameter `--resetModel` nicht verwendet, wird das bestehende Modell mit neuen Prompts erweitert und verfeinert (FineTuning).


# Training starten
Um ein Training zu starten, sollte die NLP_PARAMS Datei für den Trainingsfall optimiert bzw. eingestellt werden. Parameter für das NLP-Modell können hier definiert werden. Diese Datei wird automatisch geladen und verarbeitet.

## SIMQL_NLP_PARAMS

```
{
    "tokenizer_max_length" : 256,                   
    "temperature" : 0.2,
    "num_beams" : 4,
    "ngram_size" : 2,
    "learning_rates" : [1e-5, 2e-5, 3e-5, 5e-5],
    "learning_rate_idx" : 2,
    "epochs" : 3,
    "batch_size" : 8,
    "eval_batch_size" : 4,
    "split_size" : 0.25,
    "weight_decay" : 0.01,
    "save_total_limit" : 4,
    "save_steps" : 10000,
    "do_eval" : false,
    "top_k" : 50,
    "top_p" : 0.95,
    "pad_to_multiple_of":8
}

```

# Development Details - SIMQL_NLP_Train
## TrainingArgument Klasse
Nachfolgende Tabelle zeigt eine Auflistung der möglichen Parameter, deren Default-Werte und 'best practise' Werte.

| Parameter                     | Default          | Best Practice                                           | Beschreibung |
|-------------------------------|------------------|---------------------------------------------------------|--------------|
| **output_dir**                | N/A              | Ein eindeutiger, beschreibender Pfad (z.B. "./results/t5_experiment1") | Pfad, in dem Checkpoints, Logs und Modelle gespeichert werden. |
| **evaluation_strategy**       | "no"             | "epoch" oder "steps"                                    | Bestimmt, wann während des Trainings evaluiert wird. |
| **learning_rate**             | 5e-5             | 3e-5 bis 1e-4                                           | Lernrate für den Optimierer. |
| **per_device_train_batch_size** | 8               | 16 oder 32                                              | Batchgröße pro Gerät beim Training. |
| **per_device_eval_batch_size**  | 8               | 16 (bei ausreichend Speicher)                           | Batchgröße pro Gerät bei der Auswertung. |
| **num_train_epochs**          | 3.0              | 3 bis 5                                                 | Anzahl der Trainingsepochen. |
| **weight_decay**              | 0.0              | 0.01 bis 0.1                                            | Gewichtungsverfall zur Regularisierung. |
| **logging_dir**               | "runs/"          | Gleich wie `output_dir` oder Unterverzeichnis           | Verzeichnis für Trainingslogs. |
| **logging_steps**             | 500              | 10 bis 100                                              | Häufigkeit des Loggings in Schritten. |
| **save_steps**                | 500              | 1000 bis 2000                                           | Häufigkeit des Speicherns von Checkpoints. |
| **save_total_limit**          | N/A              | 2 bis 5                                                 | Maximale Anzahl der gespeicherten Checkpoints. |
| **seed**                      | 42               | 42 (Konsistenz)                                         | Seed für Reproduzierbarkeit. |
| **gradient_accumulation_steps** | 1               | 2 oder 4                                                | Schritte zur Gradientenakkumulation. |
| **fp16**                      | False            | True (bei unterstützter Hardware)                       | 16-Bit-Präzision für schnellere Inferenz. GPU muss vorhanden sein |
| **eval_accumulation_steps**   | N/A              | 8 bis 16                                                | Gradientenakkumulation bei der Auswertung. |
| **do_train**                  | False            | True                                                    | Ob das Training durchgeführt wird. |
| **do_eval**                   | False            | True                                                    | Ob das Modell während des Trainings evaluiert wird. |
| **warmup_steps**              | 0                | 500 bis 1000                                            | Aufwärmschritte für die Lernrate. |
| **report_to**                 | "all"            | "tensorboard", "wandb", je nach Tool                    | Ziel für Trainingsmetriken. |
| **remove_unused_columns**     | True             | True                                                    | Entfernt ungenutzte Spalten aus dem Datensatz. |
| **overwrite_output_dir**      | False            | True (bei fortlaufendem Training)                       | Überschreibt das Ausgabeverzeichnis. |
| **metric_for_best_model**     | N/A              | "eval_loss", "accuracy" je nach Aufgabe                 | Metrik zur Bestimmung des besten Modells. |
| **load_best_model_at_end**    | False            | True                                                    | Lädt das beste Modell am Ende des Trainings. |
| **greater_is_better**         | True             | True (für höhere Metriken wie Accuracy)                 | Ob eine höhere Metrik besser ist. |
| **resume_from_checkpoint**    | N/A              | Pfad zum letzten Checkpoint                             | Fortsetzen des Trainings von einem Checkpoint. |

## Trainer Klasse
der eigentliche Trainer für unser Modell

| Parameter                | Default            | Best Practice                                                        | Bemerkung |
|--------------------------|--------------------|----------------------------------------------------------------------|-----------|
| **model**                | N/A                | Verwende ein vortrainiertes Modell passend zur Aufgabe.              | Das Modell, das trainiert wird. |
| **args**                 | N/A                | Passe `TrainingArguments` an die Bedürfnisse des Trainings an.       | Trainingsargumente als `TrainingArguments`-Objekt. |
| **data_collator**        | None               | Nutze spezialisierte Collators für Tokenisierung und Padding.        | Funktion, die Batches erstellt; wichtig für unterschiedliche Eingabeformate. |
| **train_dataset**        | None               | Verwende einen gut vorbereiteten und bereinigten Datensatz.          | Der Datensatz für das Training. |
| **eval_dataset**         | None               | Nutze einen separaten, validierten Datensatz für die Auswertung.     | Der Datensatz für die Evaluation während des Trainings. |
| **tokenizer**            | None               | Nutze den zur Aufgabe passenden Tokenizer, oft den des Modells.      | Wichtig für die Konsistenz zwischen Modell und Eingabedaten. |
| **model_init**           | None               | Kann verwendet werden, um das Modell mit spezifischen Parametern zu initialisieren. | Funktion zur Initialisierung des Modells. |
| **compute_metrics**      | None               | Implementiere benutzerdefinierte Metriken, die für die Aufgabe relevant sind. | Funktion zur Berechnung von Evaluationsmetriken. |
| **callbacks**            | None               | Nutze Callbacks wie `EarlyStopping` für eine bessere Trainingssteuerung. | Liste von Callback-Funktionen, die während des Trainings aufgerufen werden. |
| **optimizers**           | (AdamW, None)      | Verwende `AdamW` und bei Bedarf angepasste Lernraten-Scheduler.      | Tuple bestehend aus (Optimizer, Scheduler). |
| **preprocess_logits_for_metrics** | None     | Kann für spezielle Aufgaben angepasst werden, um Metriken korrekt zu berechnen. | Funktion zur Vorverarbeitung der Logits für die Metrikberechnung. |
| **kwargs**               | None               | Gebe zusätzliche Parameter spezifisch für besondere Bedürfnisse an.  | Weitere zusätzliche Parameter, die spezifisch für den Trainer sein können. |

### trainer.evaluate()
Die Funktion trainer.evaluate() in der transformers-Bibliothek wird verwendet, um das Modell auf einem Evaluierungsdatensatz zu bewerten. Sie führt eine Evaluierung der Modellleistung durch, indem sie Metriken wie den Loss oder andere benutzerdefinierte Metriken auf dem bereitgestellten Evaluierungsdatensatz berechnet.

Diese Methode verarbeitet das Modell auf dem Evaluierungsdatensatz und gibt eine Reihe von Metriken zurück, die dir helfen, die Qualität des Modells auf Daten zu beurteilen, die es noch nicht gesehen hat.

| **Parameter**          | **Default Wert**    | **Best-Practice-Wert** | **Beschreibung**                                                                                                                                                          |
|------------------------|---------------------|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `eval_dataset`         | `None`              | Dein Evaluierungsdatensatz | Der Datensatz, auf dem das Modell evaluiert wird. Wenn nicht angegeben, wird der Datensatz verwendet, der während des Trainings als Evaluierungsdatensatz übergeben wurde. |
| `ignore_keys`          | `None`              | `None`                  | Bestimmt, welche Schlüssel im Modell-Output ignoriert werden sollen. Kann nützlich sein, wenn der Output des Modells zusätzliche Informationen enthält, die irrelevant sind.|
| `metric_key_prefix`    | `"eval"`            | `"eval"`                | Der Präfix, der den Evaluierungsmesswerten in der Rückgabe hinzugefügt wird (z.B. `eval_loss`, `eval_accuracy` usw.).                                                      |
| `max_length`           | Modell-spezifisch   | Modellabhängig          | Maximale Länge der Eingabe/Generierung. Kann nützlich sein, um die Generierungslänge zu begrenzen.                                                                         |
| `num_beams`            | Modell-spezifisch   | `5` oder `8`            | Anzahl der Beams für die Beam Search während der Generierung. Wird oft in Seq2Seq-Modellen wie T5 oder BART verwendet. Mehr Beams verbessern die Genauigkeit, kosten aber mehr Rechenleistung.  |
| `length_penalty`       | `1.0`               | `1.0`                  | Strafterm für längere Sequenzen während der Generierung. Werte kleiner als 1.0 begünstigen kürzere Sequenzen, Werte größer als 1.0 begünstigen längere Sequenzen.         |
| `predict_with_generate`| `False`             | `True`                 | Bestimmt, ob die Generierungsfunktion (`generate`) verwendet wird, um während der Evaluierung Vorhersagen zu treffen. Wird oft bei Seq2Seq-Modellen verwendet.            |


## DataCollator Klasse
data_collator = DataCollatorForSeq2Seq()

| **Parameter**            | **Default Wert** | **Best-Practice-Wert** | **Beschreibung**                                                                                                                                                      |
|--------------------------|------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tokenizer`              | -                | Dein genutzter Tokenizer | Der Tokenizer, der verwendet wird, um die Sequenzen aufzufüllen (Padding) und zu tokenisieren.                                                                       |
| `model`                  | `None`           | Dein genutztes Modell   | Das Seq2Seq-Modell, das verwendet wird, um modellabhängige Tokenisierungs- und Padding-Einstellungen zu berücksichtigen.                                              |
| `padding`                | `True`           | `True` oder `"longest"` | Bestimmt, ob die Sequenzen gepaddet werden. Optionen: `True` (dynamisch paddet), `"longest"` (auf längste Sequenz im Batch paddet), `"max_length"` (auf feste Länge). |
| `max_length`             | `None`           | Nur bei Bedarf setzen   | Maximale Länge der Sequenzen nach dem Padding. Wird verwendet, wenn alle Sequenzen auf eine feste Länge gebracht werden sollen.                                        |
| `pad_to_multiple_of`     | `None`           | Potenz von 2 (z.B. 8, 16) | Padded Sequenzen auf ein Vielfaches dieser Zahl. Wird oft für Hardware-Optimierung verwendet.                                                                         |
| `label_pad_token_id`     | `-100`           | `-100`                  | Der Token-ID-Wert, der für das Padding der Labels verwendet wird. Labels mit `-100` werden in den meisten Modellen beim Loss ignoriert.                               |
| `ignore_pad_token_for_loss` | `True`        | `True`                  | Bestimmt, ob Padding-Token bei der Berechnung des Loss ignoriert werden.                                                                                              |
| `return_tensors`         | `"pt"`           | `"pt"` oder `"tf"`      | Bestimmt das Format der zurückgegebenen Tensoren. Optionen: `"pt"` für PyTorch, `"tf"` für TensorFlow, `"np"` für NumPy.                                              |
