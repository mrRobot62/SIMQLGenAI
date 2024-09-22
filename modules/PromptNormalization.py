from spellchecker import SpellChecker


class PromptNormalization:
    """ 
    Führt eine Normalizierung des prompts durch und führt auch eine Fehlerkorrektur durch
    """
    def __init__(self, language='de'):
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words(['Stichtag', 'Metamesspunkt', 'MMP', 'MP', 'CREF'])

    def preprocess_prompt(self, prompt:str) -> str:
        """
        Führt ein PreProcessing des prompts durch. Um Robuster zu sein, wird der prompt in 
        kleinbuchstaben umgewandelt.
        Wichtig ist später im Modell muss die User-Eingabe ebenfalls in Kleinbuchstaben umgewandelt werden

        ggf. noch noch weitere PreProcessing Dinge hinzu
        :return prompt
        """
        prompt = prompt.lower()

        return prompt
    
    def correct_spelling(self, prompt:str) -> str:
        """ 
        Führt eine Rechtschreibkorrektur (wortweise) und gibt den korrigiert prompt zurück

        ACHTUNG in der Version 0.8.1 gibt es eine Reihe von Unzulänglichkeiten, daher wir aktuell
        keine Rechtschreibkorrektur durchgeführt
        :return prompt inkl. Rechtschreibkorrektur
        """
        #corrected_prompt = " ".join([self.spell.correction(word) for word in prompt.split()])
        #corrected_prompt = prompt
        return corrected_prompt
    

# test
normalize = PromptNormalization(language='de')
raw_prompt = "Verwende den jetzigen Stichtag und den vroletzten Stichtag und nutze MP1 und MP2 oder MP_123"
preprocessed_prompt = normalize.preprocess_prompt(raw_prompt)
corrected_prompt = normalize.correct_spelling(preprocessed_prompt)
print(f"Original Prompt     : '{raw_prompt}'")
print(f"Normalized Prompt   : '{preprocessed_prompt}'")
print(f"Normalized Prompt   : '{corrected_prompt}'")