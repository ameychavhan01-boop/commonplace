"""Display text -> spoken text for Kokoro (numbers, years, money, acronyms)."""
import re

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

def n2w(n):
    n = int(n)
    if n < 0: return "minus " + n2w(-n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000:
        r = ONES[n // 100] + " hundred"
        return r + (" " + n2w(n % 100) if n % 100 else "")
    for div, name in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= div:
            r = n2w(n // div) + " " + name
            return r + (" " + n2w(n % div) if n % div else "")

def year2w(y):
    y = int(y)
    if 2000 <= y <= 2009: return "two thousand" + (" " + ONES[y - 2000] if y > 2000 else "")
    hi, lo = divmod(y, 100)
    if lo == 0: return n2w(hi) + " hundred"
    if lo < 10: return n2w(hi) + " oh " + ONES[lo]
    return n2w(hi) + " " + n2w(lo)

ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth",
       "nine": "ninth", "twelve": "twelfth"}
def ordinal(n):
    w = n2w(n)
    parts = re.split(r"([ -])", w)
    last = parts[-1]
    if last in ORD: last = ORD[last]
    elif last.endswith("y"): last = last[:-1] + "ieth"
    else: last = last + "th"
    parts[-1] = last
    return "".join(parts)

def num_words(s):
    s = s.replace(",", "")
    if "." in s:
        a, b = s.split(".")
        return n2w(int(a)) + " point " + " ".join(ONES[int(d)] for d in b)
    return n2w(int(s))

REPL = [
    (r"\bNifty 50\b", "Nifty Fifty"),
    (r"\bOBV\b", "O B V"),
    (r"\bRSI\b", "R S I"),
    (r"\bMACD\b", "M A C D"),
    (r"\bCNBC\b", "C N B C"),
    (r"\bCOT\b", "C O T"),
    (r"\bU\.S\.", "U S"),
    (r"\bW\. D\. Gann\b", "W D Gann"),
    (r"\bJohn J\. Murphy\b", "John J Murphy"),
    (r"\bRhea\b", "Ray"),
    (r"\bX's and O's\b", "Xs and Os"),
    (r"\bV-reversal\b", "V reversal"),
    (r"\bV-shapes\b", "V shapes"),
    (r"\bV-Spikes\b", "V spikes"),
]

def spoken(text):
    t = text
    for a, b in REPL: t = re.sub(a, b, t)
    # money
    t = re.sub(r"\$([\d,]+(?:\.\d+)?)", lambda m: num_words(m.group(1)) + " dollars", t)
    # percent
    t = re.sub(r"([\d,]+(?:\.\d+)?)\s?%", lambda m: num_words(m.group(1)) + " percent", t)
    # ordinals
    t = re.sub(r"\b(\d+)(st|nd|rd|th)\b", lambda m: ordinal(int(m.group(1))), t)
    # years (4 digits, no comma)
    t = re.sub(r"\b(1[6-9]\d\d|20\d\d)\b", lambda m: year2w(m.group(1)), t)
    # other numbers
    t = re.sub(r"\b\d[\d,]*(?:\.\d+)?\b", lambda m: num_words(m.group(0)), t)
    t = t.replace("&", " and ")
    return re.sub(r"\s+", " ", t).strip()

if __name__ == "__main__":
    for s in ["On the 24th of March, 2020, India's Nifty 50 touched 7,511.", "23.9 percent", "$73,800 and $100,000",
              "1884 1902 2008 2011 1990", "the 31st of August", "OBV is 170", "$126,000 to $57,700", "38 and 62 percent"]:
        print(spoken(s))
