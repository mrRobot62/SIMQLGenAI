
import random
import json
import os
from pathlib import Path

# Define the base DSL script template
dsl_template = """
mmp {group}
    register "{group}"

    section measurement:
        v{mp1} = reference "{mp1}"
        v{mp2} = reference "{mp2}"
        
    section variables:
        {var1}
        {var2}
        {result}
    
    section logic:
        {var1} = load data(refArgument=[v{mp1}], refdates=[{refdate}], range={idxRange}, qualityLevel="{quality1}", environment="{env1}")
        {var2} = load data(refArgument=[v{mp2}], refdates=[{refdate}], range={idxRange}, qualityLevel="{quality1}", environment="{env1}")
        {result} = compute data(variables=[{var1}, {var2}], math={math})
    
    section result:
        save {result}

end;
"""

# Possible values for placeholders
groups = ["MMP1234", "MMP2345", "MMP3456", "MMP5678", "MMP7890","MMP100","MMP200","MMP300","MMP400","MMP500","MMP600"]
measure_points = ["MP1", "MP2", "MP3", "MP4","MP5","MP6","MP6","MP7","MP8","MP9","MP10","MP11","MP12","MP13","MP14","MP15"]
variables = ["vData1", "vData2", "vData3", "vData4", "vTmp1", "vTmp2", "vTmp3", "vTmp4"]
results = ["vResult", "vSave", "vData"]
qualities = ["U4", "UF", "LAT", "AT"]
ranges= ['LATEST','FIRST','ALL']
environments = ["tuc1", "tuc2", "biap_tuc1","biap_tuc2","dev01"]
math_operations = ["sum", "max", "minus", "mult", "agg","stdev", "div","plus"]
ref_dates = ['CREF', 'CREF-1', 'CREF-2', 'QREF', 'QREF-1', 'QREF-2']
mapRefDates = [{'aktuellen':'CREF'}]

# Function to generate examples based on the DSL template
def generate_dsl_examples_json(n):
    examples = []
    for _ in range(n):
        group = random.choice(groups)
        mp1 = random.choice(measure_points)
        mp2 = random.choice(measure_points)
        var1 = random.choice(variables)
        var2 = random.choice(variables)
        result = random.choice(results)
        quality1 = random.choice(qualities)
        quality2 = random.choice(qualities)
        env1 = random.choice(environments)
        env2 = random.choice(environments)
        math = random.choice(math_operations)
        idxRange=random.choice(ranges)
        refdate=random.choice(ref_dates)
        dsl_script = dsl_template.format(
            group=group,
            mp1=mp1,
            mp2=mp2,
            var1=var1,
            var2=var2,
            result=result,
            quality1=quality1,
            quality2=quality2,
            env1=env1,
            env2=env2,
            math=math,
            idxRange=idxRange,
            refdate=refdate
        )
        
        text_description = [
            f"Registriere einen MMP {group}. Verwende die Messpunkte {mp1} und {mp2}. addiere die Daten mit {math}. Speichere das Ergebnis in {result}",
            f"Entwerfe einen Metamesspunkt {group}. Verwende die Messpunkte {mp1} und {mp2}. Lade die daten aus {env1}. Berechne das Ergebnis mit {math} und speichere in {result} ",
            f"Baue einen MMP {group}. Nutze die Messpunkte {mp1} und {mp2}. Lade die daten aus {env1}. Berechne das Ergebnis mit {math} und speichere in {result} ",
            f"Registriere den MMP {group}. Nutze die Messpunkte {mp1} und {mp2}. Lade Daten mit der Qualitätsstufe {quality1} aus der Umgebung {env1}. Berechne das Ergebnis mit {math}",
            f"Generiere die MMP {group}. Nutze die Messpunkte {mp1} und {mp2}. Berechne die {math} der Variablen und speichere das Ergebnis als {result}.",
            f"Erstelle einen MMP {group}. Verwende die Messpunkte {mp1} und {mp2} zum Stichtag {refdate} und verrechne diese mit {math}. Das Ergebnis soll in {result} gespeichert werden.",
            f"MMP {group}. Messpunkte {mp1} und {mp2} per Stichtag {refdate}, Nutze {math}. Speichere {result}.",
            f"Erstelle einen Metamesspunkt {group}. Verwende die Messpunkte {mp1} und {mp2} zum Stichtag {refdate}  und berechne diese mit {math}. Speichere {result}",
            f"Neuer MMP {group}, zwei Messpunkte {mp1}, {mp2}, Stichtag {refdate}, range={idxRange}, math={math}",
            f"Neuer MMP {group}, nutze diese Messpunkte {mp1}, {mp2}, verwende Stichtag {refdate}, range={idxRange}, math={math}. Speichere {result}",
        ]

        """ 
                text_description = (
                    f"Registriere die Messpunktgruppe {group}. Verwende die Messpunkte {mp1} und {mp2}. "
                    f"Lade Daten mit den Qualitätsstufen {quality1} und {quality2} aus den Umgebungen {env1} und {env2}. "
                    f"Berechne die {math} der Variablen und speichere das Ergebnis als {result}."
                )
        """


        examples.append({
            "text": random.choice(text_description),
            "code": dsl_script.strip()
        })
        if (_ % 100) == 0:
            print(f"Trainingssätze: {_:8d}")
    return examples

# Generate 10000 examples
examples = 2000
generated_examples = generate_dsl_examples_json(examples)

# Save examples as JSON
json_path = "genai_training_data/simql_data"
json_file = f"dsl_examples_{examples}.json"
json_file = os.path.join(json_path, json_file)

with open(json_file, 'w') as json_file:
    json.dump(generated_examples, json_file, indent=2)


"""
erstelle einen MMP4711 mit zwei Messpunkten MP1 und MP2. Nutze die AGG Funktoin und speichere das Ergebnis



"""