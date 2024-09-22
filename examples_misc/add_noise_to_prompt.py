import random
import string

def add_noise_to_prompt(prompt, noise_level=0.1):
    """
    Fügt zufälliges Rauschen in einen Prompt ein, indem Buchstaben oder Zeichen an zufälligen Positionen eingefügt werden.

    :param prompt: Der Eingabetext (Prompt), in den Rauschen eingefügt werden soll.
    :param noise_level: Der Anteil an Zeichen, die als Rauschen eingefügt werden sollen (zwischen 0 und 1).
    :return: Der modifizierte Prompt mit Rauschen.
    """
    prompt_list = list(prompt)  # Konvertiere den Prompt in eine Liste von Zeichen
    num_chars_to_add = int(len(prompt) * noise_level)  # Berechne die Anzahl der Rauschen-Zeichen
    pass
    for _ in range(num_chars_to_add):
        # Wähle eine zufällige Position im Prompt und ein zufälliges Zeichen aus (Buchstaben, Ziffern oder Sonderzeichen)
        position = random.randint(0, len(prompt_list) - 1)
        random_char = random.choice(string.ascii_letters + string.digits + string.punctuation)
        
        # Füge das zufällige Zeichen an der zufälligen Position im Prompt ein
        prompt_list.insert(position, random_char)
    
    return ''.join(prompt_list)

# Beispielnutzung
original_prompt = "Bitte Kreiere einen Metamesspunkt und nutze folgenden Registrierungsnamen '{mmp_name}"
noisy_prompt = add_noise_to_prompt(original_prompt, noise_level=0.05)
print(f"Original    : {original_prompt}")
print(f"Mit Rauschen: {noisy_prompt}")
