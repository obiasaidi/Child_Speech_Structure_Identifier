import spacy
import benepar
import pandas as pd

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)

# Upload the data to process
data_cleaned = pd.read_csv("/Users/robiatualaddawiyah/Documents/College/Thesis_Project/Data/CHILDES/English/childes_cleaned.csv")  # Please adjust your dir

# Parsing children speech
data_cleaned['doc_objects'] = data_cleaned['cleaned_speech'].apply(lambda text: nlp(text))

print("Parsing DONE!")

sentence_parsed = data_cleaned[data_cleaned['doc_objects'].apply(structure.sent_segmentation)]

sentence_parsed['constituency_tree'] = sentence_parsed['doc_objects'].apply(structure.parse_const)

# Structure Identification
sentence_parsed['structure'] = sentence_parsed['doc_objects'].apply(structure.structure_idf)

print(sentence_parsed.head())
sentence_parsed.to_csv("/Users/robiatualaddawiyah/Documents/College/Year_2/LPT/NLP_project/Data/data_with_structure.csv")

print("DONE!!!")