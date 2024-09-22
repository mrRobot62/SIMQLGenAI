def generate_format_string(values):
    """
    Generiert einen Format-String basierend auf der Anzahl der Einträge im Array.
    
    :param values: Ein Array mit Werten, die in den Format-String eingefügt werden sollen.
    :return: Der dynamisch generierte Format-String und der formatierte String mit den Werten.
    """
    # Erzeuge einen dynamischen Format-String mit der richtigen Anzahl von Platzhaltern
    format_string = ', '.join([f'{{{i}}}' for i in range(len(values))])
    
    # Wende den Format-String auf die Werte an
    result_string = format_string.format(*values)
    
    return format_string, result_string

# Beispielnutzung
values = ["A", "B", "C", "E", "F"]
values = ["A", "B", "C", "E", "F","G","H","I"]

format_string, result_string = generate_format_string(values)

print("Dynamischer Format-String:", format_string)
print("Formatierter String:", result_string)
