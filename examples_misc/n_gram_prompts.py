import random
from nltk.util import ngrams
from collections import defaultdict

# Wörterbuch für N-Gram Ersetzungen
n_gram_replacements = {
    2: {  # Bigramme
        ("lade", "die"): ["importiere die", "hole die", "abrufe die"],
        ("lade", "daten"): ["importiere informationen", "hole daten", "abrufe daten"],
        ("nutze", "daten"): ["verwende daten", "gebrauche informationen", "setze daten ein"],
        ("lese", "daten"): ["extrahiere daten", "scanne daten", "entnehme informationen"]
    },
    3: {  # Trigramme
        ("lade", "die", "daten"): ["importiere die daten", "hole die informationen", "lade alle daten"],
        ("nutze", "die", "daten"): ["verwende die informationen", "gebrauche die daten", "setze die daten ein"]
    }
}

def replace_n_grams(prompt, n=2):
    """
    Ersetzt N-Gramme im Prompt durch vordefinierte Alternativen.

    :param prompt: Der Eingabetext (Prompt), der analysiert und durch N-Gramme ersetzt werden soll.
    :param n: Die Anzahl der Wörter pro N-Gramm (z.B. 2 für Bigramme, 3 für Trigramme).
    :return: Ein neuer Prompt mit den ersetzten N-Grammen.
    """
    words = prompt.lower().split()  # Den Prompt in einzelne Wörter aufteilen und in Kleinbuchstaben konvertieren
    n_gram_list = list(ngrams(words, n))  # Erzeuge N-Gramme aus dem Prompt

    # Neuer Prompt, der aufgebaut wird
    new_prompt = []
    i = 0

    while i < len(words):
        # Prüfe, ob die nächsten N-Wörter ein N-Gramm ergeben, das ersetzt werden soll
        current_n_gram = tuple(words[i:i + n])
        if current_n_gram in n_gram_replacements.get(n, {}):
            # Wähle eine zufällige Ersetzung für das N-Gramm aus
            replacement = random.choice(n_gram_replacements[n][current_n_gram])
            new_prompt.append(replacement)
            i += n  # Überspringe die Anzahl der Wörter im N-Gramm
        else:
            # Wenn kein N-Gramm-Ersatz vorhanden ist, behalte das Originalwort bei
            new_prompt.append(words[i])
            i += 1

    return ' '.join(new_prompt)

# Beispielnutzung
original_prompt = "Lade die Daten für die Analyse."
n_gram_replaced_prompt = replace_n_grams(original_prompt, n=2)  # Bigramme ersetzen
print(f"Original        : {original_prompt}")
print(f"N-Gram Ersetzt  : {n_gram_replaced_prompt}")
