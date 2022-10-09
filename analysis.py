import pickle
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer, TweetTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
import contractions, re, string

stop_words = set(stopwords.words("english"))
tokenizer = TweetTokenizer()
lemmatizer = WordNetLemmatizer()
with open("NBModel", 'rb') as f:
    analyzer = pickle.load(f)

def clean(text: str):
    # remove numbers
    text = re.sub(r"\d+", "", text)
    # expand contraction
    text = contractions.fix(text)
    #remove the retweet sign
    text = re.sub(r"^(RT)", "", text)
    # remove links
    text = re.sub(r"(ftp|https?)://\S+", "", text)
    # remove mentions
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    # remove hashtags
    text = re.sub(r"#\w+", "", text)
    # remove punctuations
    sub_txt = r"[" + re.escape(string.punctuation) + r"]"
    text = re.sub(sub_txt, "", text)
    return text.strip()

def lemmatize_sentence(token: list):
    sentence = []
    for word, tag in pos_tag(token):
        if tag.startswith("NN"):
            tag = "n" # noun
        elif tag.startswith("V"):
            tag = "v" # verb
        elif tag.startswith(("RB")):
            tag = "r" # adverb
        else:
            tag = "a" # adjective
        sentence.append(lemmatizer.lemmatize(word, tag))
    return sentence

def remove_stopwords(token: list):
    cleaned_up = []
    for word in token:
        if len(word) > 0 and word not in string.punctuation and word.lower() not in stop_words:
            cleaned_up.append(word.lower())
    return cleaned_up

def analyze(text: str) -> str:
    text = clean(text)
    tokenized_text = tokenizer.tokenize(text)
    lemmatized_text = lemmatize_sentence(tokenized_text)
    cleaned_text = remove_stopwords(lemmatized_text)
    return analyzer.classify(dict([(token, True) for token in cleaned_text]))

if __name__ == "__main__":
    print(analyze(r"""Atiku's campaign strategy up North is rather shameful. You can't go about mouthing empty rhetorics about being the "unifier" and then have your people peddling the most hateful and divisive lies all in the name of political campaign."""))