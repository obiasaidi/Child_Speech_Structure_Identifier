def struct_idf(input):
    doc = nlp(inp) # skip this if the input is already spaCy doc object
    structure_counts = []  # List to store structure found
    
    for sent in doc.sents: 
        parse_string = sent._.parse_string  # Get the const parsing in Penn Treebank format (string)
        tree = Tree.fromstring(parse_string) # Convert the string into tree object
        # tree.pretty_print()  # Visualizes the parse tree
        print(parse_string)
        #print(tree.height())  # extract the height of the tree
        
        
        def add_structure_counts(struct_name):
            if struct_name not in structure_counts:
                structure_counts.append(struct_name)
            

        # WH QUESTIONS WITH AUX_INV
        def wh_q_aux_inv(node):
            # Ensure the input is tree object
            if not isinstance(node, Tree):
                return False 

            if node.label() == 'SBARQ': # Traverse the tree looking for a node labeled 'SBARQ'
                has_wh = False # Initialize the non-existence of WH node
                wh_word = None # Initialize wh_word
                sq_node = None # Initialize sq_node
                
                for child in node: 
                    if isinstance(child, Tree): # Make sure if the child is a node not string
                        if child.label() in {'WHNP', 'WHADVP'}:
                            has_wh = True # Identify the existence of WH node
                            wh_word = child.leaves()[0]  # Get the WH word 
                        elif child.label() == 'SQ':
                            sq_node = child # Identify the aux-inv bcs sometimes it's labeled SQ but no aux-inv
                            
                if has_wh and sq_node:
                    # Sometimes SQ is labeled without aux-inv so this is needed to do
                    leaf_pos = None # Initialize leaf_pos to retrieve the pos of the first leaf (word) of SQ node
                    for word in sq_node.leaves(): # .leaves() returns all terminal (leaf) words from the tree
                        spacy_token = next((token for token in sent if token.text == word), None)  # Retrieve the first word of sq_node leaves
                        if spacy_token: # if spacy_token is not None
                            leaf_pos = spacy_token.pos_ # Identify the part of speech of the spacy_token
                            #print(f"Leaf word: {word}, POS from SpaCy: {spacy_token.pos_}")
                            break
                                 
                    if leaf_pos == 'AUX': # Make sure the SQ has aux indicating the sentence involve aux-inv
                        if wh_word == 'why':  # Check if the WH word is 'why'
                            add_structure_counts("why_q_aux_inv")
                            return True
                        else:
                            add_structure_counts("wh_q_aux_inv")
                            return True 
                    else:
                        add_structure_counts("wh_q_no_aux_inv")
                        return True
            
            # Check nested wh_q_aux_inv structure
            for child in node:
                if wh_q_aux_inv(child):
                    return True
                
            return False
        
        
        # WH QUESTIONS WITHOUT AUX INV
        def wh_q_no_aux_inv(node):
            if not isinstance(node, Tree): # Ensure the input is instance of the class Tree
                return False # If the node is not a Tree, the function exits

            if node.label() == 'SBARQ': # Traverse the tree looking for a node labeled 'SBARQ'
                has_wh = False # Initialize the non-existence of WH node
                
                for child in node:  # For each child in the node SBARQ
                    if isinstance(child, Tree):  # Make sure the child is an instance of Tree object not a leaf (string)
                        if child.label() in {'WHNP', 'WHADVP'}:  # Identify WH nodes
                            has_wh = True # Assign WH nodes into has_wh
                        elif child.label() in {'S', 'NP'} and has_wh:  # Identify S and NP nodes after WH nodes
                            add_structure_counts("wh_q_no_aux_inv") 
                            return True # Stop further processing since the structure has been identified

            # Check nested wh_q_no_aux_inv structure
            for child in node:
                if wh_q_no_aux_inv(child):
                    return True 
                
            return False
        
        
        # YES/NO QUESTIONS WITH AUX_INV
        
        # The inside_sbarq flag tracks whether it is operating inside an SBARQ context as it moves through the tree
        # It is needed to exclude SQ node under SBARQ node
        def yn_q_aux_inv(node, inside_sbarq=False):
            if not isinstance(node, Tree):  # Ensure the input is instance of the class Tree
                return False  # If the node is not a Tree, the function exits


            # Check if the current node is 'SBARQ', assign inside_sbarq as True
            if node.label() == 'SBARQ': 
                inside_sbarq = True # Identify SBARQ node to later exclude it
                
            # Check if the current node is 'SQ' and not the child of 'SBARQ'    
            if node.label() == 'SQ' and not inside_sbarq:  # not inside_sbarq to exclude SQ node under SBARQ node
                leaf_pos = None  # Initialize leaf_pos to retrieve the pos of the first leaf (word) of SQ node
                for word in node.leaves():  # .leaves() returns all terminal (leaf) words from the tree
                    spacy_token = next((token for token in sent if token.text == word), None)  # Retrieve the first word of sq_node leaves next(x,y)
                    if spacy_token:  # if spacy_token is not None
                        leaf_pos = spacy_token.pos_  # Identify the part of speech of the spacy_token
                        #print(f"Leaf word: {word}, POS from SpaCy: {spacy_token.pos_}")
                        break

                if leaf_pos == 'AUX':  # Make sure the SQ has aux indicating the sentence involve aux-inv
                    add_structure_counts("yn_q_aux_inv")
                    return True
                else:
                    add_structure_counts("yn_q_no_aux_inv")
                    return True

            # Check nested yn_q_aux_inv structure
            for child in node:
                if yn_q_aux_inv(child, inside_sbarq):
                    return True

            return False

        
        # YES/NO QUESTIONS NO AUX_INV
        def yn_q_no_aux_inv(node):
            if not isinstance(node, Tree):  # Ensure the input is instance of the class Tree
                return False  # If the node is not a Tree, the function exits

            if node.label() == 'S':  # Check if the current node is 'S'
                found_np = False  # Initializing no NP found to later identify it
                found_vp = False  # Initializing no VP found to later identify it
                # q_mark = '?' in node.leaves()
                
                for child in node:  # for each child of the node 'S'
                    if isinstance(child, Tree): # Ensure the child is an instance of Tree object not a leaf (string)
                        if child.label() == 'NP':  # Check if the child is NP
                            found_np = True  # Identify NP
                        elif child.label() == 'VP' and found_np:  # Check the child is VP and occur after NP
                            found_vp = True  # Identify VP after NP under S

                # Ensure both NP and VP are found under S and check for '?'
                if found_vp: # If there's VP after NP under S
                    # Check if '?' exists in the leaves of the current 'S' node
                    if '?' in node.leaves():
                        add_structure_counts("yn_q_no_aux_inv")  # add 'yn_q_no_aux_inv' to add_structure_counts
                        return True # Stop further processing since the structure has been identified
                    
            # Check nested yn_q_aux_inv structure
            for child in node:
                if yn_q_no_aux_inv(child):
                    return True

            return False
        

        def imperative(node):
            if not isinstance(node, Tree):  # Ensure the input is an instance of the class Tree
                return False  # If the node is not a Tree, the function exits

            if node.label() == 'S':  # Check if the current node is S
                found_vp = False  # Initialize VP to identify it later, found_vp here means a vp found without any precedence of NP

                for child in node:  # Iterate through the children of S
                    if isinstance(child, Tree):  # Ensure the input is an instance of the class Tree
                        # Defining NP found as well as ensuring no VPs following it
                        if child.label() == 'NP':  # If NP is found
                            if not found_vp:  # check whether VP appeared following NP. not found_VP means there is VP following NP (so it will return False later)
                                return False  # Return False
                        elif child.label() == 'VP':  # If a VP is found
                            found_vp = True  # Mark that VP has been found
                            
                            # Check if to-inf is present under VP
                            if any(isinstance(grandchild, Tree) and grandchild.label() == 'TO' for grandchild in child):  # Check if there is a node (an instance of Tree) under VP labelrd 'TO'
                                return False  # Return False 

                            # Check if a verb (base, VB for inf form) is found in VP, even if there are other elements
                            if any(isinstance(grandchild, Tree) and grandchild.label() == 'VB' for grandchild in child):
                                add_structure_counts("imp")  # add imperative into add_structure_counts
                                return True  # Stop further processing since the structure has been identified

            # Check nested imperative structure
            for child in node:
                if imperative(child):
                    return True

            return False

        
        # SV WITH NON-FINITE MODAL
        def sv_modal(node):
            if not isinstance(node, Tree): # If the input is not an instance of the class Tree
                return False  # Return False
            
            # Q: why no initialization for if node.label() == 'S'
            # A: not to restrict the starting node to be S node only
            
            found_np = False # Initializing the absence of NP to identify it later
            for child in node: # for each child of any node
                if isinstance(child, Tree):  # Ensure the input is an instance of the class Tree
                    if child.label() in {'NP', 'NN'}:  # if found NP or NN
                        found_np = True  # Identify the presence of NP or NN
                    elif child.label() == 'VP' and found_np:  # if found VP after NP
                        found_md = False  # Initializing the absence of MD to later identify it
                        for grandchild in child: # for each grandchild ('grandchild' means the immidiate child of VP)
                            if isinstance(grandchild, Tree) and grandchild.label() == 'MD': # if a Tree instance labeled MD found under VP
                                found_md = True  # Identify the presence of MD under VP
                            elif isinstance(grandchild, Tree) and grandchild.label() == 'VP' and found_md:  # if found VP after found MD under VP
                                
                                add_structure_counts("sv_modal")  # Add "sv_modal" to structure_counts
                                return True  # Stop further processing since the structure has been identified

                            
            # Check nested sv_modal structure
            for child in node:
                if sv_modal(child):
                    return True

            return False
        
        
        # SV SIMPLE
        def sv(node):
            if not isinstance(node, Tree):  # If the input is not an instance of the class Tree
                return False  # Return False
            
            if node.label() != 'S':  # If the node label is not 'S'.
                return False  # Return False
            
            # Check if the entire node contains a question mark in its leaves to avoid sv_simple identification in no-aux-inv questions
            has_q_mark = '?' in node.leaves()  # Assign '?' identification to has_q_mark
            
            found_np = False  # Initialize the absence of NP to later identify it

            for child in node:  # For any child under S
                if isinstance(child, Tree):  # Ensure the input is an instance of the class Tree
                    if child.label() == 'NP':  # if found NP
                        found_np = True  # Identify NP
                    elif child.label() == 'VP' and found_np and not has_q_mark:  # If found VP after NP and there's no question mark '?' in the leaves
                        if not any(isinstance(grandchild, Tree) and grandchild.label() == 'MD' for grandchild in child):  # Check if no nodes under VP labeld MD ('not' negates both isinstance and .label())
                            add_structure_counts("sv_simple")  # Add "sv_simple" to structure_counts
                            return True # Stop further processing since the structure has been identified
                    # elif child.label() == 'VP' and found_np and has_q_mark:
                    #     add_structure_counts("yn_q_no_aux_inv")  # Add "sv_simple" to structure_counts
                    #     return True
      
                    
                    
            # Check nested sv_simple structure
            for child in node:
                if sv(child):
                    return True
                    # return False

            return False
        
        
        # FINITE_NEGATION
        def fin_neg(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False
            
            found_verb = False  # Initialize the absence of verb to later identify it
            has_neg = False  # Initialize the absence of negation to later identify it
            
            neg_markers = {'not', "n't", "ain't"}  # Assign negation words to neg_markers
            if any(neg in node.leaves() for neg in neg_markers):  # Check if there is neg words in the leaves
                has_neg = True  # Identify has_neg if negation words found in the leaves
            
            for child in node:  # For each child of any node
                if isinstance(child, Tree):  # Ensure the node is an instance of the class Tree
                    if child.label() in {'VBD', 'VBP', 'VBZ', 'MD'}:  # Check if the labels found
                        found_verb = True  # Identify the verbs exist
                    elif child.label() == 'RB' and found_verb and has_neg:  # If found RB, verbs mentioned in the same depth, and a neg word in the leaves (but i think the order of found_verb and RB is ignoed here)
                        add_structure_counts("fin_neg")  # Add 'fin_neg' to structure_counts
                        return True  # Stop further processing since the structure has been identified
                    
            # Check nested fin_neg structure
            for child in node:
                if fin_neg(child):
                    return True

            return False


        # NON-FINITE TO-INFINITIVE
        def to_inf(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False
            
            if node.label() == 'S': # if found S
                for child in node: # for each child of the node S
                    if isinstance(child, Tree) and child.label() == 'VP': # if it is a tree instance and labeled VP
                        has_to = False # Initializing the absence of TO
                        # Check if there's "TO" in the VP
                        for grandchild in child: # for each grandchild ('grandchild' refers to the immidiate child of VP)
                            if isinstance(grandchild, Tree) and grandchild.label() == 'TO': # if found TO under VP
                                has_to = True  # Assign node TO under VP to has_to
                            elif isinstance(grandchild, Tree) and grandchild.label() == 'VP' and has_to: #  if found VP (under VP) and node has_to is True (meaning it's been encountered before)
                                add_structure_counts("to_inf")  # Add "to_inf" to structure_counts
                                return True # Stop further processing since the structure has been identified

            # Check nested to_inf structure
            for child in node:
                if to_inf(child):
                    return True
            
            return False
        
        
        # SINV
        def sinv(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False
            
            if node.label() == 'SINV':  # if found SINV
                add_structure_counts("SINV")  # add "SINV" to structure_counts
                return True  # Stop further processing since the structure has been identified
            
            return False  # Return False if no SINV found throughout the tree
        
        
        # PREPOSED ADVERB
        def prep_adv(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False
            
            found_rb = False  # Initialize the absence of RB to later identify it
            found_pp = False  # Initialize the absence of PP to later identify it
            found_np = False  # Initialize the absence of NP to later identify it

            for child in node:  # For any child in the current node (the label for root node does not matter)
                if isinstance(child, Tree):  # Ensure the node is a tree instance
                    if child.label() == 'ADVP':  # if a child labeled ADVP
                        for advp_child in child:  # Inspect the children of ADVP
                            if advp_child.label() == 'RB':  # If the children of ADVP is RB
                                found_rb = True  # Identify RB (RB is for adverb of manner like happily etc)
                    elif child.label() == 'PP':  # if a child labeled PP
                        found_pp = True  # Assign the presence of PP into found_pp
                    elif child.label() == 'NP' and (found_rb or found_pp):  # check if NP found after found_rb or found_pp True (there's NP after adverb/pp)
                        found_np = True  # Assign ADVP/PP NP into found_np
                    elif found_np and child.label() == 'VP':  # check if VP found after found_np True (make sure the order of prep adv like ADVP/PP NP VP)
                        add_structure_counts("prep_adv")  # Add "prep_adv" to structure_counts
                        return True  # Stop further processing since the structure has been identified
                    
            # Check nested prep_adv structure
            for child in node:
                if prep_adv(child):
                    return True

            return False 



        # RELATIVE CLAUSES
        def rc(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False

            if node.label() == 'NP':  # Check if the current node is labeled 'NP' as relative clauses should occur under NP
                has_np_in_np = any(child.label() == 'NP' for child in node if isinstance(child, Tree)) # If found NP in the children of node NP assign it into has_np_in_np
                if has_np_in_np:  # if has_np_in np True
                    for child in node: # for each child of the node  of first NP
                        if isinstance(child, Tree) and child.label() == 'SBAR':  # If node SBAR found after has_np_in_np True (indicating there is NP and SBAR in the same depth level)
                            found_whnp = False  # Initializing the absence of WHNP to later identify it
                            for sbar_child in child:  # For each child of node SBAR
                                if isinstance(sbar_child, Tree) and sbar_child.label() == 'WHNP':  # if a SBAR child is a tree instance and labeled WHNP
                                    found_whnp = True  # Assign to found_whnp (Identify the presence of WHNP)
                                elif isinstance(sbar_child, Tree) and sbar_child.label() == 'S' and found_whnp:  # If found SBAR child labeled S after found_whnp is True
                                    
                                    # CHECK FOR and OR
                                    has_np = any(child.label() == 'NP' for child in sbar_child if isinstance(child, Tree)) # If S has a child NP, assign it to has_np
                                    has_vp = any(child.label() == 'VP' for child in sbar_child if isinstance(child, Tree)) # If S has a child VP, assign it to has_vp

                                    if not has_np and has_vp:  # if there is only vp in S's children
                                        add_structure_counts("sr")  # add 'sr' to structure_counts
                                        return True  # Stop further processing since the structure has been identified

                                                                        
                                    if has_np and has_vp: # if there are NP and VP as S's children indicating OR (I think the order of NP and VP doesn't matter here)
                                        for np_child in sbar_child: # this naming 'sbar_child' is very confusing but actually the code is correct -___-
                                            if isinstance(np_child, Tree) and np_child.label() == 'NP':  # if found a tree instance labeled NP under S
                                                has_prp = any(grandchild.label() == 'PRP' for grandchild in np_child if
                                                              isinstance(grandchild, Tree))  # if found a tree instance labeled PRP under NP, assign to has_prp
                                                if has_prp:  # if has_prp True
                                                    add_structure_counts("or_no_intv")  # Add 'or_no_intv' to structure_counts
                                                    return True  # Stop further processing since the structure has been identified
                                                if not has_prp:  # if the child node of NP not labeled PRP (if has_prp is False)
                                                    add_structure_counts("or_intv")  # Add 'or_intv' to structure_counts
                                                    return True  # Stop further processing since the structure has been identified
                                                                            
                                    

            # Check nested relative clauses structure
            for child in node:
                if rc(child):
                    return True

            return False

        
        # CLAUSAL EMBEDDING --> this only identifies clause embedded to a VP (VP selects CP)
        def selection(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False

            if node.label() == 'VP':  # Check if a node labeled VP
                found_verb = False  # Initializing the absence of verbs

                for child in node:  # For each child of VP
                    if isinstance(child, Tree):  # Ensure the child of VP is a tree instance (not string)
                        if child.label() in {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}:  # If found a verb under VP
                            found_verb = True  # Assign the presence of verb into found_verb
                        elif child.label() == 'SBAR' and found_verb:  # If found SBAR and found_verb is True
                            found_to = False  # Initialize the absence of found_to to later identify it
                            has_vp_in_sbar = False  # To track if there's a VP inside S

                            # Check the children of S for 'TO' and 'VP' --> Because if they are present, they are not finite embedded clause, they are considered as embedded to-inf
                            for sbar_child in child:  # For any child of SBAR
                                if isinstance(sbar_child, Tree):  # Ensure if the SBAR child is a tree instance
                                    if sbar_child.label() == 'TO':  # Check for 'TO' within the SBAR node
                                        found_to = True
                                    elif sbar_child.label() == 'VP':  # Check for 'VP' within the SBAR node
                                        has_vp_in_sbar = True

                            # If found TO and VP under SBAR, return False
                            if found_to or has_vp_in_sbar:
                                return False

                            # If no 'TO' and no 'VP' in the SBAR node, classify it as an embedded clause
                            add_structure_counts("emb_clause")  # Add 'emb_clause' to structure_counts
                            return True  # Stop further processing since the structure has been identified
                        

            # Recursively check all children
            for child in node:
                if selection(child):
                    return True
                
            return False


        # SUBORDINATE CLAUSE
        def subordinate_clause(node):
            if not isinstance(node, Tree):  # If the node is not an instance of the class Tree
                return False  # Return False

            
            has_q_mark = '?' in node.leaves()  # If found question mark in the leaves, asign it to has_q_mark (to avoid miss-identification for no-aux-inv wh questions)
            found_wh_in = False  # Initialize WHNP, WHADVP, and IN nodes to later identify it
            
            for child in node:  # For each child of a node
                if isinstance(child, Tree):  # Ensure the child node is a tree instance
                    if child.label() in {'WHNP', 'WHADVP', 'IN'}:  # If a child of a node labeled one of those mentioned
                        found_wh_in = True  # Identify the presence of WHNP/WHADVP/IN
                    elif child.label() == 'S' and found_wh_in and not has_q_mark:  # if found the node S as a child of any node after found_wh_in is True and if there's no question mark in the leaves
                        add_structure_counts("sub_clause")  # Add  'sub_clause' to structure_count
                        return True  # Stop further processing since the structure has been identified

            
            # Recursively check all children (if there is a nested sub_clause structure
            for child in node:
                if subordinate_clause(child):
                    return True

            return False

        # Check each structure independently and append to `output` if matched.
        wh_q_aux_inv(tree)
        wh_q_no_aux_inv(tree)
        yn_q_aux_inv(tree)
        yn_q_no_aux_inv(tree)
        imperative(tree)
        sv_modal(tree)
        sv(tree)
        fin_neg(tree)
        to_inf(tree)
        sinv(tree)
        prep_adv(tree)
        rc(tree)
        selection(tree)
        subordinate_clause(tree) 

        # If no matches, classify as "Other Structure"
        if not structure_counts:
            add_structure_counts("Other_Structure")
    
    return structure_counts  # Return structure_counts for the main function so the output would be the sentence structure and the number of its occurances

df_filter['structure'] = df_filter['parsed'].apply(struct_idf)
df_filter['parse_trees'] = sdf_filter['parsed'].apply(lambda doc: ' '.join([sent._.parse_string for sent in doc.sents])) # to retrieve const parse tree into the df
