import re

def remove_multiple_spacing(line):
    line = re.sub(r'\s{2,}', ' ', line) # remove multiple spacing
    line = re.sub(r'\n{2,}', '\n', line) # remove multiple breaks
    return line

def fix_word(line):
    line = re.sub(r" em ", " them ", line)
    line = re.sub(r" ya |^ya ", " you ", line)
    line = re.sub(r" ta |^ta ", " to ", line)
    line = re.sub(r" hafta |^hafta ", " have to ", line)
    line = re.sub(r" sposta |^sposta ", " supposed to ", line)
    line = re.sub(r" hadta |^hadta ", " had to ", line)
    line = re.sub(r" hasta |^hasta ", " has to ", line)
    line = re.sub(r" needta |^needta ", " need to ", line)
    line = re.sub(r" useta |^useta ", " used to ", line)
    line = re.sub(r" outa |^outa ", " out of ", line)
    line = re.sub(r" oughta |^oughta ", " ought to ", line)
    line = re.sub(r"going a |gonna ", "going to ", line)
    line = re.sub(r"wanna ", "want to ", line)
    return line


def preprocess(line):
    line = ' '.join(line.strip().split())  # Remove extra spaces
    line = line[6:]  # Remove the first 6 characters
    line = line.lower()  # Convert text to lowercase
    line = re.sub(r' \d+_\d+-?', '', line.strip())  # Remove timestamp
    line = re.sub(r'\[\+ \w+?\]', '', line)  # Remove patterns like [+ text]
    line = re.sub(r'\[- hun\].*[.!?]', '', line)  # Remove the whole string contain '[- hun]'

    # Grammar Error
    line = re.sub(r'\s*\[\*\sm:0(\w+).*?\]', r'\1', line)  # Handle [m:0 ] missing reg form
    line = re.sub(r'[\wʃʌɪɯəɪˈʤʧ@]+\s*\[\*\s(\w{2,})\]', r'\1', line)  # Handle patterns like [* forgot] and [* that]
    line = re.sub(r"\[\*(\s*.*)?\]", '', line)  # Remove patterns like [*] and [* text]
    line = re.sub(r"\S+\s*\[:\s*(.+?)\]", r'\1 ', line)  # Handle patterns like 'a [: of]' and 'beated [: beat]'

    # Handle [=!  ] [=?  ] [%  ]
    line = re.sub(r'\[=!\s.+?\]', '', line)  # Remove patterns like [=! wolf noises]
    line = re.sub(r'two months \[=\? (too much)\]', r'\1', line)  # Handle string 'two months [=? too much]'
    line = re.sub(r'\S+?\s*\[=\?\s*(.+?)\]', r'\1', line)  # Handle patterns like 'bobby [=? bottle]'
    line = re.sub(r"\[[%=].+?\]", '', line)  # Remove patterns like [% text] or [= text]

    # Handle Ampersand &
    line = re.sub(r'&=0', '', line)  # Remove patterns like &=0
    line = re.sub(r"&[*=~+-][\w'@^-]+(\s*[.?!])?", '', line)  # Remove patterns like &* &= &~ &+ &-

    line = re.sub(r'@\S+?', '', line)  # Remove string with @
    line = re.sub(r'\$\S+?', '', line)  # Remove string with $
    line = re.sub(r'\(\.+\)', ',', line)  # Replace (.) (..) (...) with ,
    line = re.sub(r'[‡„]', ',', line)  # replace „ and ‡ with ,
    line = re.sub(r'\(|\)', '', line)  # Remove () in patterns like op(en) to be like open
    line = re.sub(r':', '', line)  # Remove : in patterns like mi:lk
    line = re.sub(r'(?<=\w)_(?=\w|\s)', ' ', line)  # Remove _ in patterns like teddy_bear
    line = re.sub(r'\+\.{2,3}', '', line)  # Remove +.. or +...
    line = re.sub(r'\[\?\]|\[!+\]', '', line)  # Remove [!][!!][?]
    line = re.sub(r'↓', '', line)  # Remove ↓
    line = re.sub(r'0', '', line)  # Remove 0

    line = re.sub(r'\[<\]|\[>\]', '', line)  # Remove [<] and [>]
    line = re.sub(r'\+\+', '', line)  # Remove ++
    line = re.sub(r'\+\^', '', line)  # Remove +^ quick uptake
    line = re.sub(r'\+<|\+\^|\^', '', line)  # Remove +< and +^ and ^

    # Handle repetition and retracing [/] [//]
    line = re.sub(r"<.+?>(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\S+?(\s+\[.+?\])?\s+\[/+\]", "", line)
    line = re.sub(r"\s*\[/+\]", "", line)

    line = re.sub(r"[<>]", '', line)  # Remove left <>
    line = re.sub(r'\+/|\+,|\+"/?', '', line)  # Remove +/ +, and +"/ +"
    line = re.sub(r'^\s*,\s*', '', line)  # Remove comma in the beginning
    line = re.sub(r'(,\s*)+', ', ', line)  # Remove multiple comma
    # line = re.sub(r'\b(w{2,}|x{2,}|y{2,})\b', '<UNK>', line)  # Substitute www xxx and yyy with <UNK>

    line = re.sub(r'^[\s.?!]*$', '', line)  # Remove space . ? ! in lines with only space . ? !
    line = fix_word(line)  # Fix words like hafta sposta
    line = re.sub(' ([.!?,])', r'\1', line)  # Remove single space before . ! and ?
    line = re.sub(r"\b(\w+('\w+)?)(?:\s+\1)+\b", r"\1", line) # Remove repeated tokens/words
    line = line.strip()
    line = remove_multiple_spacing(line)
    return line #+ "\n"

# Preprocess children speech
df['cleaned_speech'] = df['ori_speech'].apply(preprocess)


# Drop duplicate lines
data = df.drop_duplicates(subset=['cleaned_speech'])

# Dropping unnecessary speech for line
patterns = [
    r'^\s*[.?!]*\s$',                  # Speech with only punctuation                  
    r"^\s*[\w@'-]*(\s*[.!?])?$",       # Speech with only one word         
    r"^\s*[\w@\'-]*\s*xxx\s*[.!?]*$",  # Speech with only one word and xxx
    r"^\s*[\w@\'-]*\s*yyy\s*[.!?]*$",  # Speech with only one word and yyy
    r"^\s*[\w@\'-]*\s*www\s*[.!?]*$",  # Speech with only one word and www
    r'^\s*xxx\s*[.!?]*$',              # Speech with only xxx         
    r'^\s*yyy\s*[.!?]*$',              # Speech with only yyy 
    r'^\s*www\s*[.!?]*$',              # Speech with only www 
    r'^\s*$'                           # Empty or only-space string
]

patterns_to_drop = '|'.join(patterns)

cleaned = data[~data['cleaned_speech'].str.match(patterns_to_drop, na=False)]

print("process done!!")
