# SIMQLGenAI
 GenerativeAI für die Erstellung von SIMQL-DSL Language files

## VisualCode - launch.json

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "(1) SIMQL_PromptGenerator",
            "type": "debugpy",
            "request": "launch",
//            "program": "${file}",
            "program": "SIMQL_prompt_generator.py",
            "console": "integratedTerminal",
            "args": [
                "--output_path",    "genai_training/prompts",
                "--template_path",  "genai_training/simql_templates",
                "--input_path",     "genai_training/misc",
                "--input_file",     "simql_prompt_templates.json",
//                "--prompt_type",    "['mmp', 'mp2', 'mp3', 'mp4','ld2_refdate', 'simple2' ]",
                "--prompt_type",    "['mmp','mp2','mp3','loaddata_2mp', 'loaddata_3mp','simple_2mp', 'simple_3mp' ]",
//                "--prompt_type",    "['simple_2mp']",
                "--number_of_rows", "200",
                "-v"
            ]
        },
        {
            "name": "(2) SIMQL_TrainDataGeneratorV2",
            "type": "debugpy",
            "request": "launch",
//            "program": "${file}",
            "program": "SIMQL_TrainDataGeneratorV2.py",
            "console": "integratedTerminal",
            "args": [
                "-v",
                "-n", "10",
                "--path_prompt",    "genai_training/prompts",
                "--path_template",  "genai_training/simql_templates",
                "--out_path",       "genai_training/out_data",
//                "--prompt_file",    "prompts_shorts2.txt",
//                "--prompt_file",    "prompts_shorts_fehlerhaft.txt",
                
                "--read_all",
//                "-s",
//              "-c",

            ]
        },
        {
            "name": "(3) SIMQL NLP Training",
            "type": "debugpy",
            "request": "launch",
//            "program": "${file}",
            "program": "SIMQL_NLP_Train_V1.py",
            "console": "integratedTerminal",
            "args": [
                "-v",
                "--path_train_data",    "genai_training/out_data",
                "--output_dir",         "genai_model/training_mmp",
//                "--output_dir",         "genai_model/t5_small_orig",
                "--train_files",        "['train_data_20240923_1813_0011410.json']",                
                "--nlp_param_file",     "simql_nlp_params.json",
                "--tokens_file",        "simql_tokens.txt",
                //"--resetModel",
                "--train_model",        "T5-small",
                // "--train_model",        "T5-base",
            ]
        },
        {
            "name": "(4) SIMQL NLP V2",
            "type": "debugpy",
            "request": "launch",
//            "program": "${file}",
            "program": "SIMQL_NLP_V2.py",
            "console": "integratedTerminal",
            "args": [
                "-v",
                "--path_train_data",    "genai_training/out_data",
                "--path_model_out",     "genai_out",
                "--path_model",         "genai_model/training_mmp",
                "--simql_model_path",   "simql_model",
                "--simql_model_file",   "model.tx",
                "--nlp_param_file",     "simql_nlp_params.json",
                "--translate_prompt_file", "translate_prompt_mmp.txt"
            ]
        },
    ]
}

```

 siehe README_TRAIN.md

