import random

# Wörterbuch für Synonyme
synonyms = {
    "lade": ["importiere", "hole", "abrufe"],
    "daten": ["information", "informationen", "daten"],
    "für": ["zur", "für die", "zwecks"],
    "analyse": ["auswertung", "untersuchung", "analyse"],
    "nutze": ["verwende", "gebrauche", "benutze"],
    "lese": ["extrahiere", "scanne", "entnehme"]
}

def paraphrase_prompt(prompt):
    """
    Paraphrasiert einen Prompt, indem zufällige Synonyme für bestimmte Wörter eingefügt werden.
    
    :param prompt: Der Eingabetext (Prompt), der paraphrasiert werden soll.
    :return: Ein paraphrasierter Prompt.
    """
    words = prompt.split()  # Den Prompt in einzelne Wörter aufteilen
    paraphrased_words = []
    
    # Ersetze jedes Wort im Prompt durch ein zufälliges Synonym, falls vorhanden
    for word in words:
        lower_word = word.lower()  # Wörter auf Kleinbuchstaben prüfen
        if lower_word in synonyms:
            # Wähle zufällig ein Synonym aus dem Wörterbuch
            paraphrased_words.append(random.choice(synonyms[lower_word]))
        else:
            # Wenn kein Synonym vorhanden ist, behalte das Originalwort
            paraphrased_words.append(word)
    
    # Setze die Wörter wieder zu einem Satz zusammen
    paraphrased_prompt = ' '.join(paraphrased_words)
    return paraphrased_prompt

# Beispielnutzung
original_prompt = "Lade die Daten für die Analyse."
paraphrased_prompt = paraphrase_prompt(original_prompt)
print(f"Original        : {original_prompt}")
print(f"Paraphrasiert   : {paraphrased_prompt}")
