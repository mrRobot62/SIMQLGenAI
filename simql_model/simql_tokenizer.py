class ConstantParser:
    def __init__(self, input_file,):
        self.input_file = input_file
        self.tokens = []

    def read_file(self):
        with open(self.input_file, 'r') as file:
            lines = file.readlines()
        return lines

    def parse_constants(self):
        lines = self.read_file()
        for line in lines:
            line = line.strip()
            # Überprüfe, ob die Zeile das richtige Format hat und mit einem Semikolon endet
            if line.endswith(';'):
                # Teile die Zeile an ':', um den CONSTANTE Namen und den Wert zu trennen
                parts = line.split(':')
                if len(parts) == 2:
                    # Entferne das Semikolon und spalte an '|', um die lowerCase und UPPERCase zu erhalten
                    values = parts[1].replace(';', '').split('|')
                    if len(values) == 2:
                        lower_case, upper_case = values[0].strip(), values[1].strip()
                        # Füge die Werte der Tokenliste hinzu
                        self.tokens.extend([eval(lower_case), eval(upper_case)])
                        #self.tokens.extend([eval(lower_case)])

    def sort_tokens(self):
        # Sortiere die Tokens alphabetisch
        self.tokens.sort()

    def save_tokens(self, output_file='tokens.txt'):
        with open(output_file, 'w') as file:
            for token in self.tokens:
                file.write(token + '\n')

# Beispielhafte Nutzung
parser = ConstantParser('simql_model/constants.tx')
parser.parse_constants()
parser.sort_tokens()
parser.save_tokens()
