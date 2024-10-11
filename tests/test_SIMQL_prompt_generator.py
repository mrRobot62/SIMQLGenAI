import pytest
import argparse
import os
from SIMQL_prompt_generator import PromptGenerator

class TestPromptGenerator:


    @pytest.fixture
    def setup(self):
        """Set up the TraindataGeneratorV2 object for testing."""
        # Erstelle einen ArgumentParser
        parser = argparse.ArgumentParser(description="Trainingsdatengenerator V2")
        parser.add_argument('--input_path', required=True, help='Pfad zur PROMPT-JSON Augmentationdatei')
        parser.add_argument('--template_path', required=True, help='Pfad zur SIMQL-Templates')
        parser.add_argument('--input_file', required=True, help='JSON-Augmentationdatei')
        parser.add_argument('--output_path', required=True, help='Pfad wo die generierte Dateien gespeichert werden')
        parser.add_argument('--output_file', default='prompt_{ts}_{prompt_type}.txt', help="Ausgabedateien die generiert werden (Template-Filename)")
        parser.add_argument('--number_of_rows', type=int, default=10, help='Ungefähre Anzahl an generierten Datensätzen')
        parser.add_argument('--prompt_types', required=True, type=lambda s: s.strip("[]").split(','), help="Liste zu generierenden Prompt-Typs. (siehe JSON-Augmentation-File)")
        parser.add_argument('-v', default=1, action='count', help='Verbosity -v -vv -vvv')

        # Simuliere die Argumente
        self.test_args = [
            #'-v ',
            # 0, 1
            '--output_path',    'genai_training/prompts',
            # 2, 3
            '--template_path',  'genai_training/simql_templates',
            # 4, 5 
            '--input_path',     'genai_training/misc', 
            # 6, 7
            '--input_file',     'simql_prompt_templates.json',
            # 8, 9
            '--prompt_type',    "['mmp','mp2','mp3','loaddata_2mp', 'loaddata_3mp','simple_2mp', 'simple_3mp' ]",
            # "--prompt_type",    "['simple_2mp']",
            # 10, 11
            '--number_of_rows', '100'
            ]
        args = parser.parse_args(self.test_args)

        self.generator = PromptGenerator(args)

    def test_init(self, setup):
        """Test the initialization of the class."""
        assert self.generator is not None

    def test_load_input_data(self, setup):
        """ Prüft _load_input_data() """
        # Übergeben werden muss der Pfad für Generierungs-JSON-Datei 
        file_path = os.path.join(self.test_args[5], self.test_args[7] )
        data = self.generator._load_input_data(file_path)
        # sind überhaupt Daten vorhanden
        assert data is not None
        # prüfen ob alle geforderten keys die als Parameter übergeben wurd
        # in der JSON-Datei enthalten sind.
        prompt_types = eval(self.test_args[9])
        for ptype in prompt_types:
            assert ptype in data


    def test_prepare_internal_data_lists(self, setup):
        """ prüft der _prepare_internal_data_lists() """
        # 
        file_path = os.path.join(self.test_args[5], self.test_args[7] )
        data = self.generator._load_input_data(file_path)
        self.generator.data = data
        #
        # interne Listen füllen basieren auf den gewünschten Prompt-Type
        prompt_types = eval(self.test_args[9])
        for ptype in prompt_types:
            self.generator.prompt_type = ptype
            self.generator._prepare_internal_data_lists()
            assert len(self.generator.options_intro1) > 0
            assert len(self.generator.options_intro2) >= 0
            assert len(self.generator.options_intro3) >= 0
    
        pass

