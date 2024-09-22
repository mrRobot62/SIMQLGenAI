def remove_stopwords(text, stopwords):
    """
    Entfernt potenzielle deutsche Stop- und Füllwörter aus einem Text.
    
    :param text: Der Eingabetext, aus dem die Stopwörter entfernt werden sollen.
    :param stopwords: Eine Liste von Stopwörtern, die entfernt werden sollen.
    :return: Der Text ohne die Stopwörter.
    """
    # Text in einzelne Wörter aufteilen
    words = text.split()

    # Nur Wörter behalten, die nicht in der Stopwörter-Liste sind
    filtered_words = [word for word in words if word.lower() not in stopwords]
    
    # Zusammensetzen des gefilterten Textes
    return ' '.join(filtered_words)

# Beispiel von potenziellen deutschen Stop- und Füllwörtern
stopwords = [
    "der", "die", "das", "ein", "eine", "und", "oder", "aber", "nicht", "noch", 
    "zu", "in", "mit", "von", "auf", "an", "für", "aus", "bei", "wie", "über", 
    "nach", "dass", "so", "nur", "auch", "um", "im", "dem", "des", "ist", 
    "am", "wenn", "dann", "doch", "noch", "schon"
]

# Beispielnutzung
text = """
Erstelle einen Metamesspunkt '{mmp_alias}' und referenziere auf '{mmp_name}'. 
Dieser MMP verwendet zwei Messpunkte '{mp1}' und '{mp2}'.Die Daten sollen aus dem {environment} geladen werden.
Lade jeweils den {data_range} Datensatz und nutze die {math} Funktion.
Speichere das Ergebnis.
"""
filtered_text = remove_stopwords(text, stopwords)
print(f"Original    : {text}")
print(f"Gefiltert   : {filtered_text}")

# Ergebnis:
# Erstelle einen Metamesspunkt '{mmp_alias}' referenziere '{mmp_name}'. 
# Dieser MMP verwendet zwei Messpunkte '{mp1}' '{mp2}'. Daten sollen {environment} geladen werden. 
# Lade jeweils den {data_range} Datensatz nutze {math} Funktion. Speichere Ergebnis.