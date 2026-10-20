import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    # Keep useful technical symbols such as c++, c#, .net
    text = re.sub(r"[^a-z0-9+#.\-/ ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
