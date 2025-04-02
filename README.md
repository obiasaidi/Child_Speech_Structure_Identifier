# Child_Speech_Structure_Identifier
This project aims to build an automated system that can identify syntactic structure in children speech using a rule-based approach.
The system is build on the purpose of linguistic analysis of language development in children. The rule-based syntactic structure identifier detects 14 syn structure (listed in Structure Class), following syntactic acquisition order by the Growing Tree approach ([Friedmann, Belletti, &amp; Rizzi, 2021]([url](https://doi.org/10.16995/glossa.5877))). With multilable classification, one or more structure can be assigned to a given sentence.

**Data Collection**: the data used is taken from [CHILDES English - North American data]([url](https://childes.talkbank.org/access/Eng-NA/)), using Brown and MacWhinney corpus.
The corpus contains 5 children longitudinal speech ranging from 16 - 92 months old. The data is downloaded in .cha format.  
  
**Structure class**:
1. SV simple
2. Imperative
3. Finite negation
4. SV with modal
5. SV with non-finite TO-inf
6. Non-standard WH-questions
7. Non-standard yes/no questions
8. Standard WH-questions
9. Standard yes/no questions
10. Preposed Adv
11. Subj-Verb Inversion
12. Declarative-that
13. Interrogative-if
14. Subordinate Clause

**1-preprocess** contains the codes to preprocess the dataset before being fed to the rule-based syn structure identifier.  
**2-structure_identification** contains the codes to parse, filter children speech, and the rule-based syn structure identifier.
