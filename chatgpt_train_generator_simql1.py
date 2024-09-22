import random

# Vorlagen für natürliche Sprache und zugehörige DSL-Anweisungen
base_sentences = [
    ("Registriere die Messpunktgruppe '{group}'. Erstelle eine Messungssektion mit Referenzen zu den Messpunkten '{mp1}' und '{mp2}'. Lade Daten für die neuesten Einträge, berechne die Differenz und speichere das Ergebnis als '{result}'.",
     "register '{group}'\n\nsection measurement:\n\t{mp1} = reference '{mp1}'\n\t{mp2} = reference '{mp2}'\n\tpass\n\nsection logic\n\t{result}=compute data(refArgument=[{mp1}, {mp2}], refdates=[CREF], range=LATEST, math=minus)\n\tpass\n\nsection result:\n\tsave {result}\n\nEnd"),
    ("Lade Daten mit Referenz '{ref}' und Qualitätslevel '{quality}'.",
     "vData{num} = LOAD DATA (REF={ref}, QUALITY_LEVEL='{quality}')"),
    ("Berechne die Summe der Variablen '{var1}' und '{var2}'.",
     "vResult{num} = COMPUTE DATA (VARIABLES=[{var1}, {var2}], MATH=SUM)"),
    # Weitere Vorlagen können hier hinzugefügt werden
]

# Mögliche Werte für Platzhalter
groups = ["MMP1234", "MMP2345", "MMP3456"]
refs = ["RefA", "RefB", "RefC"]
qualities = ["high", "medium", "low"]
variables = ["vVar1", "vVar2", "vVar3", "vVarA", "vVarB", "vVarC"]
measure_points = ["MP1", "MP2", "MP3", "MP4", "MP5"]
results = ["vDiffResult", "vSumResult", "vMaxResult"]
num_range = range(1, 11)

# Funktion zur Generierung von Beispielen
def generate_examples(n):
    examples = []
    for _ in range(n):
        sentence, code = random.choice(base_sentences)
        text = sentence.format(
            group=random.choice(groups),
            ref=random.choice(refs),
            quality=random.choice(qualities),
            var1=random.choice(variables),
            var2=random.choice(variables),
            mp1=random.choice(measure_points),
            mp2=random.choice(measure_points),
            result=random.choice(results),
            num=random.choice(num_range)
        )
        dsl_code = code.format(
            group=random.choice(groups),
            ref=random.choice(refs),
            quality=random.choice(qualities),
            var1=random.choice(variables),
            var2=random.choice(variables),
            mp1=random.choice(measure_points),
            mp2=random.choice(measure_points),
            result=random.choice(results),
            num=random.choice(num_range)
        )
        examples.append((text, dsl_code))
    return examples

# Generierung und Ausgabe von Beispielen
generated_examples = generate_examples(20)
for example in generated_examples:
    print(f"Natürliche Sprache: {example[0]}\nDSL Code: {example[1]}\n")
