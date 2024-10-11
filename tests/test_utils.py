import pytest
import argparse
import os
from modules.utils import *

class TestUtils:
    @pytest.fixture
    def setup(self):
        """Set up the Utils object for testing."""

    def test_init(self, setup):
        pass

    def test_split_text(self, setup):
        """ """
        text = "Generiere Messpunkt,mit CREF.verarbeite; ALL"
        words = split_text(text, " ,.;")
        assert len(words) == 6
        pass

    def test_search_key_in_array_of_dicts(self, setup):
        """ """
        d = {
            "key1" : 1,
            "key2" : "a",
            "key3" : {
                "key3_1" : 1,
                "key3_2" : "b"
            }
        }
        # key nicht vorhanden
        result =  search_key_in_array_of_dicts(d, "key3_x") 
        assert result is None or len(result) == 0
        result = search_key_in_array_of_dicts(d, "key3_1")
        assert len(result) > 0

    def test_is_key_in_array_of_dicts(self, setup):
        """ """
        pass

    def test_is_value_in_array_of_dicts(self, setup):
        """ """       
        pass

    def test_convert_to_lower_case(self, setup):
        """ """
        pass

    def test_get_dict_with_value(self, setup):
        """ """
        pass

    def test_remove_duplicates_by_prompt(self, setup):
        """ """
        pass

    def test_get_timepart(self, setup):
        """ """
        pass

    def test_load_text_file(self, setup):
        """ """
        pass

    def test_save_text_file(self, setup):
        """ """
        pass

    def test_replace_placeholders(self, setup):
        """ """
        pass

    def test_remove_entries_by_pattern(self, setup):
        """ """
        pass



