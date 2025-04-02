# Import module required
import spacy
import benepar
from nltk import Tree
import pandas as pd

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)


def sent_filter(doc):  
    target_labels = ['S', 'SBAR', 'SQ', 'SBARQ', 'VP', 'MD'] 

    def contains_target_label(tree):
        if tree.label() in target_labels:
            return True
        for child in tree:
            if isinstance(child, Tree) and contains_target_label(child):
                return True
        return False

    for sent in doc.sents:
        parse_tree = sent._.parse_string  # Get the constituency parse
        tree = Tree.fromstring(parse_tree)

df_filtered = df_cleaned[df_cleaned['parsed'].apply(sent_filter)]
        if contains_target_label(tree):
            return True

    return False
