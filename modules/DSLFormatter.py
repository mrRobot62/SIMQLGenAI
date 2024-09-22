class DSLFormatter:
    def __init__(self, indent="    "):
        """
        Initialisiert die DSLFormatter-Klasse mit der angegebenen Einrückung.

        :param indent: String, der die Einrückung darstellt (z.B. vier Leerzeichen oder ein Tab).
        """
        self.indent = indent
        # Definierte Hauptschlüsselwörter und ihre Einrückungsstufen
        self.keywords = {
            "mmp ": 0,
            "register": 1,
            "section measurements:": 1,
            "section variables:": 1,
            "section logic:": 1,
            "section result:": 1,
            "end": 0
        }

        # Extra-Schlüsselwörter und deren zugeordnete Callback-Funktionen
        self.extra_keywords = {
            "MMP ": self.format_mmp,
            "mmp ": self.format_mmp,
            "reference": self.format_reference
        }

    def format_mmp(self, line):
        """
        Formatiert das MMP-Schlüsselwort, indem das folgende Wort in der gleichen Zeile steht.

        :param line: Die Zeile, die das MMP-Schlüsselwort enthält.
        :return: Formatierte Zeile.
        """
        parts = line.split()
        return f"{parts[0]} {parts[1]}\n"

    def format_reference(self, line):
        """
        Formatiert das 'reference'-Schlüsselwort, sodass das Wort davor und das Wort danach
        in einer Zeile stehen.

        :param line: Die Zeile, die das 'reference'-Schlüsselwort enthält.
        :return: Formatierte Zeile.
        """
        parts = line.split()
        index = parts.index('reference')
        return f"{parts[index - 1]} reference {parts[index + 1]}\n"

    def format_text(self, text):
        """
        Formatiert den übergebenen Text durch Hinzufügen von Zeilenumbrüchen und Einrückungen,
        basierend auf den definierten Hauptschlüsselwörtern und Extra-Schlüsselwörtern.

        :param text: Der unformatierte Eingabetext.
        :return: Der formatierte Text als String.
        """
        formatted_lines = []
        current_indent = 0
        current_line = ""

        i = 0
        while i < len(text):
            # Prüfen, ob eine Zeile mit einem bekannten Hauptschlüsselwort beginnt
            for keyword, indent_level in self.keywords.items():
                if text[i:i+len(keyword)] == keyword:
                    # Speichern der aktuellen Zeile, falls vorhanden
                    if current_line.strip():
                        formatted_lines.append(self.indent * (current_indent + 1) + current_line.strip())
                        current_line = ""

                    # Setzen der neuen Einrückung basierend auf dem Hauptschlüsselwort
                    current_indent = indent_level
                    formatted_lines.append(self.indent * current_indent + keyword)
                    i += len(keyword)
                    break
            else:
                # Überprüfen auf extra Schlüsselwörter und ihre spezifischen Formatierungen
                for extra_keyword, callback in self.extra_keywords.items():
                    if text[i:i+len(extra_keyword)] == extra_keyword:
                        # Speichern der aktuellen Zeile, falls vorhanden
                        if current_line.strip():
                            formatted_lines.append(self.indent * (current_indent + 1) + current_line.strip())
                            current_line = ""

                        # Rufen Sie die Callback-Funktion für das extra Schlüsselwort auf
                        extra_line = text[i:].split(None, 1)[0]
                        formatted_lines.append(self.indent * (current_indent + 1) + callback(extra_line.strip()))
                        i += len(extra_keyword) + 1
                        break
                else:
                    current_line += text[i]
                    i += 1

        # Hinzufügen der letzten Zeile, falls vorhanden
        if current_line.strip():
            formatted_lines.append(self.indent * (current_indent + 1) + current_line.strip())

        return "\n".join(formatted_lines)

# Beispielnutzung der DSLFormatter-Klasse
formatter = DSLFormatter(indent="    ")  # Einrückung mit 4 Leerzeichen
input_text = "mmp MP4721 register \"MMP4721_BusinessKey\"section measurements:vMP1 reference \"MP1\"vMP2 reference \"MP2\"section variables:define x,y, vResultsection variables:define x,y,resultsection logic:x = LOAD DATA(ref=[vMP1], \"CREF\", U4, range=LATEST)y = LOAD DATA(ref=[vMP2], \"CREF\", U4, range=LATEST)vResult = COMPUTE DATA(variables=[x,y], math=MINUS)section result:save vResultend"
formatted_text = formatter.format_text(input_text)
print(formatted_text)
