import os
import pandas as pd


# Function to extract corpus names, child ages, and CHI speeches from .cha files and store it to a dataframe
def text_to_df(d_in):
    corpus = []
    files = []
    ages = []
    original_speeches = []

    for file in os.listdir(d_in):
        if file.endswith('.cha'):  # Process only .cha files
            print(".", end="")
            file_path = os.path.join(d_in, file)  # Get the full path of the file

            # Extract the file name
            file_name = file  # Just take the file name

            with open(file_path, encoding='utf8', errors='ignore') as f:
                corpus_name = os.path.basename(d_in)  # Main directory name as the corpus name
                speaker_name = ''  # Initialize child name
                child_age = ''  # Reset age for each file

                for line in f:
                    # Extract corpus names and child ages from @ID line
                    if line.startswith("@ID:") and "|CHI|" in line:
                        parts = line.split('|')
                        corpus_name = parts[1].strip()
                        child_age = parts[3].strip()

                    # Extract speeches starting with *CHI
                    if line.startswith("*CHI"):
                        ori_speech = line.strip()

                        corpus.append(corpus_name)
                        files.append(file_name)
                        ages.append(child_age)
                        original_speeches.append(ori_speech)

    # Create a dataframe
    df = pd.DataFrame({
        'corpus': corpus,  # Main directory name or extracted corpus name
        'files': files,  # File names
        'child_age': ages,  # Extracted child age
        'ori_speech': original_speeches  # List of speeches
    })

    return df
