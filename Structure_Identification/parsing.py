# Import module required
import spacy
import benepar
from nltk import Tree
import pandas as pd

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)

df_cleaned['parsed'] = df_cleaned['cleaned_speech'].apply(lambda text: nlp(text))
