import re

# def convert_to_lower_case(text, preserve_patterns):
#     """
#     Wandelt einen Text in Kleinbuchstaben (lower-case) um, behält jedoch bestimmte Inhalte unverändert.
    
#     :param text: Der Eingabetext, der umgewandelt werden soll.
#     :param preserve_patterns: Eine Liste von Regex-Mustern, die nicht umgewandelt werden sollen.
#     :return: Der umgewandelte Text mit unveränderten Inhalten gemäß den übergebenen Mustern.
#     """
    
#     # Kombiniere alle Muster zu einem einzigen Regex-Ausdruck mit einer Gruppe für jedes Muster
#     #combined_pattern = '|'.join(f'({pattern})' for pattern in preserve_patterns)
#     combined_pattern = preserve_patterns

#     # Funktion zum Ersetzen der Treffer
#     def replace_function(match):
#         # Überprüft, ob das Match zu einem Muster gehört, das nicht umgewandelt werden soll
#         for group in match.groups():
#             if group is not None:
#                 return group  # Unverändert zurückgeben
#         # Alles andere wird in Kleinbuchstaben umgewandelt
#         return match.group(0).lower()

#     # Ersetze den Text mit der kombinierten Funktion
#     result = re.sub(combined_pattern, replace_function, text, flags=re.IGNORECASE)
#     return result


import re
import re

def convert_to_lower_case(text, preserve_patterns = [r'(?<=[\"\'$#]\b)(.*?)(?=\b[\"\'$#])']):
    """
    Wandelt einen Text in Kleinbuchstaben (lower-case) um, behält jedoch bestimmte Inhalte unverändert,
    basierend auf den angegebenen Mustern.

    :param text: Der Eingabetext, der umgewandelt werden soll.
    :param preserve_patterns: Eine Liste von Regex-Mustern, die nicht umgewandelt werden sollen.
    :return: Der umgewandelte Text mit unveränderten Inhalten gemäß den übergebenen Mustern.
    """
    
    # Kombiniere alle Muster zu einem einzigen Regex-Ausdruck
    combined_pattern = '|'.join(preserve_patterns)
    #combined_pattern = preserve_patterns

    # Splitte den Text nach preserve patterns und konvertiere nur die gewünschten Teile
    result = ''
    last_end = 0

    # Iterate über alle Treffer der preserve patterns
    for match in re.finditer(combined_pattern, text):
        # Füge den Text vor dem aktuellen Match hinzu und konvertiere ihn in Kleinbuchstaben
        result += text[last_end:match.start()].lower()
        # Füge das gefundene Match unverändert hinzu
        result += match.group(0)
        # Setze den Startpunkt für den nächsten Abschnitt
        last_end = match.end()
    
    # Füge den restlichen Text nach dem letzten Match hinzu und konvertiere ihn in Kleinbuchstaben
    result += text[last_end:].lower()

    return result

# Beispielnutzung
input_text = 'Erstelle einen MMP "MP11" mit dem BusinessKey "MP11_tralala" und zusätzlich Messpunkte "MP1_A" und "MP2_A".'
input_text = "Generiere einen MMP mit dem Businesskey '{MMP_name}'"
#input_text = "Generiere einen MMP mit dem Businesskey 'MP_ABcdEF'"
#                     (?<=["'$]\b)(.*?)(?=\b["'$])
preserve_patterns = r'(?<=[\"\'$#]\b)(.*?)(?=\b[\"\'$#])' # Muster, das alles zwischen Anführungszeichen, einfache Anführungszeichen und Dollarzeichen selektiert

#output_text = convert_to_lower_case(input_text, preserve_patterns)
output_text = convert_to_lower_case(input_text)
print(output_text)  # Erwartete Ausgabe: erstelle einen mmp "MP11" mit dem businesskey "MP11_tralala" und zusätzlich messpunkte "MP1_A" und "MP2_A".

