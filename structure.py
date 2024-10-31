import spacy
import benepar
from nltk import Tree

benepar.download('benepar_en3')

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe('benepar', config={'model': 'benepar_en3'}, last=True)

# Function to get constituency parse tree (Used to check structure identification)
def parse_const(text):
    doc = nlp(text)
    return ' '.join([sent._.parse_string for sent in doc.sents])

def sent_segmentation(doc):
    target_labels = ['S', 'SBAR', 'SQ', 'SBARQ', 'VP', 'VB', 'VBP', 'VBD', 'VBZ', 'MD']

    def contains_target_label(tree):
        """Recursively check if any node in the tree has a label in target_labels."""
        if tree.label() in target_labels:
            return True
        for child in tree:
            if isinstance(child, Tree) and contains_target_label(child):
                return True
        return False

    for sent in doc.sents:
        parse_tree = sent._.parse_string  # Get the constituency parse
        tree = Tree.fromstring(parse_tree)

        # Return True if the root or any descendant has a target label
        if contains_target_label(tree):
            return True

    return False


def structure_idf(doc):
    # Ensure we are working with the parsed sentence tree from Benepar
    if doc.is_parsed and len(list(doc.sents)) > 0:
        # Use the first sentence's parse tree from doc (assuming only one sentence per doc)
        parse_tree_str = list(doc.sents)[0]._.parse_string  # Benepar stores constituency parse in this attribute

        parse_tree = Tree.fromstring(parse_tree_str)  # Convert the parse string to a tree structure

        # Main Clause Identification (starting with 'S' as the root)
        if parse_tree.label() == 'S':
            children = list(parse_tree)  # Get the immediate children of the root

            # Flags to track structure elements for various clauses
            found_NP = False
            found_VP = False

            # Iterate through top-level children of the parse tree
            for child in children:
                # Case 1: Embedded Subordinate Clause
                if child.label() == 'SBAR':
                    return "Embedded subordinate clause"

                # Check for NP and VP sequence for SV Simple or Imperative
                if child.label() == 'NP':
                    found_NP = True
                elif child.label() == 'VP':
                    if found_NP:
                        # Check if VP contains 'MD' or an embedded 'S' with specific patterns
                        for grandchild in child:
                            # Case 2: Non-finite Modal
                            if grandchild.label() == 'MD':
                                return "Non-finite Modal"

                            # Case 3: Non-finite to-inf structure
                            elif grandchild.label() == 'S':
                                found_S = True
                                for grandchild2 in grandchild:
                                    if grandchild2.label() == 'VP':
                                        found_TO = False
                                        found_nested_VP = False

                                        # Check for 'TO' and nested VP structure within VP
                                        for grandchild3 in grandchild2:
                                            if grandchild3.label() == 'TO':
                                                found_TO = True
                                            elif grandchild3.label() == 'VP' and found_TO:
                                                found_nested_VP = True
                                                break

                                        if found_TO and found_nested_VP:
                                            return "Non-finite to-inf"

                        # Default case for SV structure if no other patterns are matched
                        return "SV simple"

                    # Case 4: Imperative (when there’s no NP before VP)
                    elif not found_NP:
                        return "Imperative"

            # Case 5: Preposed-Adv (ADVP/PP before NP and VP)
            found_adv = False
            found_NP = False
            found_VP = False

            # Second loop to check for Preposed-Adv structure
            for child in children:
                if child.label() in ('ADVP', 'PP'):
                    found_adv = True
                elif child.label() == 'NP' and found_adv:
                    found_NP = True
                elif child.label() == 'VP' and found_adv:
                    found_VP = True

            if found_adv and found_NP and found_VP:
                return "Preposed Adv"

        # Relative Clauses Identification
        children = list(parse_tree)

        found_NP = False
        found_vp = False

        for child in children:
            if child.label() == 'NP':
                found_NP = True

                found_nested_NP = False
                found_SBAR = False

                for grandchild in child:
                    if grandchild.label() == 'NP':
                        found_nested_NP = True
                    elif grandchild.label() == 'SBAR':
                        if found_nested_NP:
                            found_SBAR = True

                            found_WHNP = False
                            found_S = False

                            for grandchild2 in grandchild:
                                if grandchild2.label() == 'WHNP':
                                    found_WHNP = True
                                elif grandchild2.label() == 'S':
                                    if found_WHNP:
                                        found_S = True

                                        found_NP = False
                                        found_VP = False

                                        for grandchild3 in grandchild2:
                                            if grandchild3.label() == 'NP':
                                                found_NP = True
                                            elif grandchild3.label() == 'VP':
                                                if found_NP:
                                                    found_VP = True

                                        if found_NP and found_VP:
                                            found_PRP = any(grandchild4.label() == 'PRP' for grandchild4 in grandchild3)
                                            if found_PRP:
                                                return "OR-inv"
                                            else:
                                                return "OR+inv"
                                        elif found_VP and not found_NP:
                                            return "SR"


            # Declarative and Interrogative Clauses
            elif child.label() == 'VP' and found_NP:
                found_vp = True

                # Check VP children for 'that/if' conditions
                for grandchild in child:
                    if grandchild.label() == 'SBAR':
                        found_s = False
                        found_that = False
                        found_if = False

                        for grandchild2 in grandchild:
                            if grandchild2.label() == 'IN' and grandchild2[0].lower() == 'that':
                                found_that = True
                            elif grandchild2.label() == 'IN' and grandchild2[0].lower() == 'if':
                                found_if = True
                            elif grandchild2.label() == 'S':
                                found_s = True

                        # Determine Declarative-that or Interrogative-if
                        if found_that and found_s:
                            return "Declarative-that"
                        elif found_if and found_s:
                            return "Interrogative-if"

        # If the root is 'SBAR', identify as Subordinate Clause
        if parse_tree.label() == 'SBAR':
            return "Subordinate Clause"

        # Yes/No Question Identification (root 'SQ')
        if parse_tree.label() == 'SQ':
            children = list(parse_tree)
            found_aux = False
            found_np = False

            for child in children:
                # Check for auxiliary verb first
                if child.label() in ('VBP', 'VBD', 'VBZ', 'MD'):
                    found_aux = True

                # Check for NP after auxiliary
                elif child.label() == 'NP':
                    if found_aux:
                        found_np = True

                    if found_aux and found_np:
                        return "yes/no-questions"

        # Wh-Question Identification (root 'SBARQ')
        elif parse_tree.label() == 'SBARQ':
            children = list(parse_tree)
            found_whadvp = False
            found_whnp = False
            found_sq = False
            found_why = False

            for i, child in enumerate(children):
                # Check for WHADVP (e.g., 'why')
                if child.label() == 'WHADVP':
                    whadvp_children = list(child)
                    for whadvp_child in whadvp_children:
                        if whadvp_child.label() == 'WRB':
                            if whadvp_child[0].lower() == 'why':
                                found_why = True
                            found_whadvp = True

                # Check for WHNP (e.g., 'what', 'who')
                elif child.label() == 'WHNP':
                    found_whnp = True

                # SQ or S should come after WHADVP or WHNP
                elif child.label() in ('S', 'SQ'):
                    if (found_whadvp or found_whnp) and i > 0:
                        found_sq = True
                        if found_why:
                            return "why-questions"
                        elif found_whadvp or found_whnp:
                            return "wh-questions"

        # If no other structure is identified
        return "Other Structure"