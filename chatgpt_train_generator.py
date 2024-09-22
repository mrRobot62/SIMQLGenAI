import pandas as pd

# Basis-Sätze für die Generierung von Variationen
base_sentences = [
    ("Lade Daten mit Referenz '{ref}' und Qualitätslevel '{quality}'", "vData{num} = LOAD DATA (REF={ref}, QUALITY_LEVEL='{quality}')"),
    ("Berechne die Summe der Variablen '{var1}' und '{var2}'", "vResult{num} = COMPUTE DATA (VARIABLES=[{var1}, {var2}], MATH=SUM)"),
    ("Definiere einen SLA für den Typ {type}, Tag {day}, um {time} Uhr mit dem Schlüssel '{key}'", "vSla{num} = SLA({type}, {day}, '{time}', '{key}', 0)"),
    ("Speichere die Ergebnisse in der Variablen '{output}'", "SAVE {output}"),
    ("Erstelle eine Sektion für das Ergebnis und speichere die Daten", "SECTION RESULT:\n    SAVE {resultData}"),
    ("Führe eine Aggregation mit der Funktion VMAX auf den Variablen '{var1}', '{var2}' und '{var3}' durch", "vAggResult{num} = COMPUTE DATA (VARIABLES=[{var1}, {var2}, {var3}], MATH=VMAX)"),
    ("Berechne die IQR mit einem Schwellenwert von {threshold} für die Messpunkte '{mp1}' und '{mp2}'", "vIqrResult{num} = COMPUTE DATA (REF=MPList[{mp1}, {mp2}], MATH=IQR({threshold}))"),
    ("Erstelle eine neue Variable mit der minimalen Zahl aus '{list}'", "vMinValue{num} = COMPUTE DATA (VARIABLES={list}, MATH=MIN)"),
    ("Lade Daten aus der Referenz '{ref}' für den Zeitraum von '{date_from}' bis '{date_to}'", "vData{num} = LOAD DATA (REF={ref}, REFDATES=['{date_from}', '{date_to}'])"),
    ("Kombiniere die Variablen '{var1}', '{var2}', und '{var3}' und speichere das Ergebnis in '{combinedVar}'", "vCombinedVar{num} = JOIN(VARIABLES=[{var1}, {var2}, {var3}])")
]

# Platzhalterwerte für die Sätze
refs = ["RefA", "RefB", "RefC"]
qualities = ["high", "medium", "low"]
variables = ["vVar1", "vVar2", "vVar3", "vVarA", "vVarB", "vVarC"]
types = ["AT", "KT"]
days = [1, 5, 10]
times = ["08:00", "12:00", "16:00"]
keys = ["calendar1", "calendar2"]
thresholds = [1.5, 2.0]
lists = ["vList1", "vList2"]
dates_from = ["2021-01-01", "2022-01-01"]
dates_to = ["2021-12-31", "2022-12-31"]
num_range = range(1, 11)

# Generiere 10 Varianten
data = []
for i in range(10):
    sentence, code = random.choice(base_sentences)
    text = sentence.format(
        ref=random.choice(refs),
        quality=random.choice(qualities),
        var1=random.choice(variables),
        var2=random.choice(variables),
        var3=random.choice(variables),
        type=random.choice(types),
        day=random.choice(days),
        time=random.choice(times),
        key=random.choice(keys),
        output=f"vOutput{random.choice(num_range)}",
        resultData=f"vResultData{random.choice(num_range)}",
        mp1=random.choice(variables),
        mp2=random.choice(variables),
        threshold=random.choice(thresholds),
        list=random.choice(lists),
        date_from=random.choice(dates_from),
        date_to=random.choice(dates_to),
        combinedVar=f"vCombinedVar{random.choice(num_range)}",
        num=random.choice(num_range)
    )
    data.append([f'"{text}"', f'"{code}"'])

# Erstelle DataFrame und speichere als CSV
df = pd.DataFrame(data, columns=["text", "code"])
csv_path = "/mnt/data/dsl_variants.csv"
df.to_csv(csv_path, sep='#', index=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="DSL Variants", dataframe=df)

csv_path
