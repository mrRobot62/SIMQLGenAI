import re
import fnmatch

def remove_entries_by_pattern(entry_set, regex_patterns=None, wildcard_patterns=None):
    """
    Entfernt Einträge aus einem Set, die entweder einem regulären Ausdruck oder Wildcards entsprechen.
    
    :param entry_set: Set mit Einträgen.
    :param regex_patterns: Liste von regulären Ausdrücken.
    :param wildcard_patterns: Liste von Wildcard-Strings (wie "AUTO_*").
    :return: Set ohne die Einträge, die den Mustern entsprechen.
    """
    # Wenn kein Muster vorhanden ist, gib das ursprüngliche Set zurück
    if not regex_patterns and not wildcard_patterns:
        return entry_set

    # Kompiliere die regulären Ausdrücke
    compiled_regexes = [re.compile(pattern) for pattern in regex_patterns] if regex_patterns else []
    
    # Führe das Filtern durch
    filtered_set = set()
    for entry in entry_set:
        # Überprüfe auf reguläre Ausdrücke
        if any(regex.match(entry) for regex in compiled_regexes):
            continue
        
        # Überprüfe auf Wildcard-Muster
        if any(fnmatch.fnmatch(entry, pattern) for pattern in wildcard_patterns or []):
            continue
        
        # Behalte den Eintrag, wenn er kein Muster trifft
        filtered_set.add(entry)
    
    return filtered_set

# Beispielnutzung
entries = {"AUTO_123", "MMP_456_789", "TEST_ENTRY", "MMP_1234", "AUTO_LOG", "SOME_OTHER"}

# Wildcard-Muster
wildcards = ["AUTO_*", "MMP*_*"]

# Regulärer Ausdruck
regex_patterns = [r"TEST_.*"]

# Entferne Einträge, die den Mustern entsprechen
result = remove_entries_by_pattern(entries, wildcard_patterns=wildcards, regex_patterns=regex_patterns)

print("Gefiltertes Set:", result)
