import random
import string
import re
import json
from nltk.util import ngrams

class PromptAugmentation:
    def __init__(self, synonyms_file=None, insert_words_file=None, stopwords_file=None, n_grams_file=None):
        """
        Initialisiert die PromptAugmentation-Klasse. Lädt Synonyme, Stopwörter, Einfügewörter und N-Gramme
        aus Dateien.

        :param synonyms_file: Dateiname für das Synonym-Wörterbuch (JSON).
        :param insert_words_file: Dateiname für die Einfüge-Wörter (JSON).
        :param stopwords_file: Dateiname für die Stopwörter (JSON).
        :param n_grams_file: Dateiname für die N-Gramme (JSON).
        """
        self.synonyms = self._load_data(synonyms_file) if synonyms_file else {}
        self.insert_words = self._load_data(insert_words_file) if insert_words_file else list(string.ascii_lowercase)
        self.stopwords = self._load_data(stopwords_file) if stopwords_file else ["der", "die", "das", "und", "oder", "nicht"]
        self.n_grams = self._load_data(n_grams_file) if n_grams_file else {}

    def _load_data(self, file_path):
        """
        Lädt Daten aus einer JSON-Datei.

        :param file_path: Pfad zur JSON-Datei.
        :return: Geladene Daten als Dictionary oder Liste.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _extract_protected_sequences(self, text):
        """Extrahiert und schützt Sequenzen in einfachen und doppelten Anführungszeichen."""
        pattern = r'(["\'$#])(.*?)(\1)'  # Erkenne Text zwischen '' oder ""
        protected_sequences = re.findall(pattern, text)
        return protected_sequences

    def _restore_protected_sequences(self, text, protected_sequences):
        """Stellt geschützte Sequenzen wieder her."""
        for seq in protected_sequences:
            protected_text = f'{seq[0]}{seq[1]}{seq[2]}'  # z.B. "sequence" oder 'sequence'
            text = text.replace('<PROTECTED>', protected_text, 1)
        return text

    def _protect_sequences(self, text):
        """Schützt Sequenzen in einfachen und doppelten Anführungszeichen durch Ersetzen."""
        pattern = r'(["\'])(.*?)(\1)'
        return re.sub(pattern, '<PROTECTED>', text)

    def synonym_swap(self, prompt):
        """Ersetzt Wörter durch Synonyme, falls verfügbar."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() in self.synonyms:
                words[i] = random.choice(self.synonyms[word.lower()])
        
        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def random_word_delete(self, prompt, delete_level=0.1):
        """Löscht zufällig Wörter aus dem Prompt."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        num_to_delete = int(len(words) * delete_level)
        for _ in range(num_to_delete):
            if len(words) > 1:
                del words[random.randint(0, len(words) - 1)]

        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def change_word_order(self, prompt):
        """Ändert die Reihenfolge der Wörter im Prompt."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        random.shuffle(words)

        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def random_word_include(self, prompt, include_level=0.1):
        """Fügt zufällig Wörter in den Prompt ein."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        num_to_add = int(len(words) * include_level)
        for _ in range(num_to_add):
            words.insert(random.randint(0, len(words)), random.choice(self.insert_words))

        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def add_typo(self, prompt, typo_level=0.1):
        """Fügt zufällige Tippfehler in den Prompt ein."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        def introduce_typo(word):
            if len(word) > 1:
                pos = random.randint(0, len(word) - 2)
                return word[:pos] + word[pos + 1] + word[pos] + word[pos + 2:]
            return word

        words = prompt.split()
        num_typos = int(len(words) * typo_level)
        for _ in range(num_typos):
            i = random.randint(0, len(words) - 1)
            words[i] = introduce_typo(words[i])

        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def remove_stopwords(self, prompt):
        """Entfernt deutsche Stopwörter aus dem Prompt."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        filtered_words = [word for word in words if word.lower() not in self.stopwords]

        prompt = ' '.join(filtered_words)
        return self._restore_protected_sequences(prompt, protected_sequences)

    def paraphrase(self, prompt):
        """Führt eine einfache Paraphrasierung durch (Synonymaustausch)."""
        return self.synonym_swap(prompt)

    def n_gram_replace(self, prompt):
        """Ersetzt N-Gramme im Prompt durch definierte N-Gramme."""
        protected_sequences = self._extract_protected_sequences(prompt)
        prompt = self._protect_sequences(prompt)

        words = prompt.split()
        for n in [2, 3]:
            for ngram_tuple in ngrams(words, n):
                if ngram_tuple in self.n_grams:
                    replacement = random.choice(self.n_grams[ngram_tuple])
                    idx = words.index(ngram_tuple[0])
                    words[idx:idx + n] = replacement.split()

        prompt = ' '.join(words)
        return self._restore_protected_sequences(prompt, protected_sequences)


# Beispielnutzung
# augmentor = PromptAugmentation(
#     synonyms_file='examples_misc/synonyms.json',
#     insert_words_file='examples_misc/insert_words.json',
#     stopwords_file='examples_misc/stopwords.json',
#     n_grams_file='examples_misc/n_grams.json'
# )


# Beispiele zum Testen
# prompt = """
# Erstelle einen Metamesspunkt referenziere '{mmp_name}'. 
# Dieser MMP verwendet zwei Messpunkte '{mp1}' und '{mp2}'.Die Daten sollen aus dem '{environment}' geladen werden.
# Lade für alle Daten jeweils den '{data_range}' Datensatz und nutze die '{math}' Funktion.
# """

# print("Original:", prompt)

# # Synonymaustausch
# print("Synonym Swap:\n", augmentor.synonym_swap(prompt))

# # Wortentfernung
# print("Random Word Delete:\n", augmentor.random_word_delete(prompt))

# # Wortreihenfolge ändern
# print("Change Word Order:\n", augmentor.change_word_order(prompt))

# # Zufällige Wörter einfügen
# print("Random Word Include:\n", augmentor.random_word_include(prompt))

# # Tippfehler hinzufügen
# print("Add Typo:\n", augmentor.add_typo(prompt))

# # Stopwörter entfernen
# print("Remove Stopwords:\n", augmentor.remove_stopwords(prompt))

# # Paraphrasierung
# print("Paraphrase:\n", augmentor.paraphrase(prompt))

# # N-Gram Austausch
# print("N-Gram Replace:\n", augmentor.n_gram_replace(prompt))
