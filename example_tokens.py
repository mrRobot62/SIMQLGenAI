
# Hugging Face for model, tokenizer, and a training function:
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from transformers import get_linear_schedule_with_warmup
from datasets import Dataset

from torch.utils.data import DataLoader
import torch
import json
import os

# Beispieltext
text = "Ich benötige einen MetaMesspunkt. Gib ihm den Namen MMP4471, Lade nun MP1 mit dem aktuellen Stichtag und MP2 mit dem letzten Stichtag. Bilde anschließend die Differenz und speichere das Ergebnis"
tokenizer = T5Tokenizer.from_pretrained('t5-small')

# Tokenisierung des Textes
tokens = tokenizer.tokenize(text)
token_ids = tokenizer.encode(text, add_special_tokens=True)

print("Tokens:", tokens)
print("Token IDs:", token_ids)
print("Anzahl der Tokens:", len(token_ids))