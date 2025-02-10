# Child_Speech_Structure_Identifier
This project aims for rule-based text classification to build a system that can identify children speech structure.
The project is part of [Child Synactic Development Automatic Measurement]([url](https://github.com/obiasaidi/Child-Syn-Dev-Automatic-Measurement)). This identifier is built to create training data for the Child Syntactic Development Automatic Measurement project.

**Data Collection**: the data used is taken from [CHILDES English - North American data]([url](https://childes.talkbank.org/access/Eng-NA/)), using Brown and MacWhinney corpus.
The corpus contains 5 children longitudinal speech ranging from 16 - 92 months old. The data is downloaded in .cha format.  

**CHILDES_cleaning.py**: Functions containing regular expressions to clean noises from CHILDES transcription.
  
**Structure class**:
1. SV simple
2. Imperative
3. Non-finite modal
4. Non-finite TO-inf
5. Embedded subordinate clause
6. Preposed Adv
7. Declarative-that
8. Interrogative-if
9. Subordinate Clause
10. wh-questions
11. why-question
