# Function to convert all strings to lower case and strip names of spaces
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i).strip() for i in x]
    else:
        #Check if item exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x).strip()
        else:
            return ''

def replace_space(x):
    if isinstance(x, str):
        return str.lower(x).replace(" ", "")
    else:
        return ''

def trim_str(x):
    if isinstance(x, str):
        return x.strip()
    else:
        return ''