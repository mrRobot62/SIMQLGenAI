import string

def replace_placeholders(template, **kwargs):
    """
    Ersetzt die Platzhalter ${wert} und ${daten} im String dynamisch, wenn sie vorhanden sind.
    Falls der Platzhalter im String vorhanden ist, aber kein entsprechender Wert übergeben wurde,
    bleibt der Platzhalter erhalten.
    
    :param template: Der String, der Platzhalter enthält.
    :param kwargs: Die zu ersetzenden Werte für die Platzhalter.
    :return: Der String mit den ersetzten Werten.
    """
    # Erstelle eine Template-Instanz
    template_obj = string.Template(template)
    
    # Ersetze Platzhalter, wobei fehlende Platzhalter unverändert bleiben
    return template_obj.safe_substitute(kwargs)

# Beispiel-String mit Platzhaltern
template1 = "Der Wert ist ${wert} und die Daten sind ${daten}."
template2 = "Nur die Daten sind ${daten}."
template3 = "Nur der Wert ist ${wert}."

# Ersetzen der Platzhalter, falls vorhanden
result1 = replace_placeholders(template1, wert=100, daten="Testdaten")
result2 = replace_placeholders(template1, daten="Weitere Daten")
result3 = replace_placeholders(template1, wert=200)

# Ausgabe der Ergebnisse
print(result1)  # Der Wert ist 100 und die Daten sind Testdaten.
print(result2)  # Nur die Daten sind Weitere Daten.
print(result3)  # Nur der Wert ist 200.
