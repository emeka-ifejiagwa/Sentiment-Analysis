import tweepy
import analysis
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

my_format = "%Y-%m-%d %H:%M:%S"
AGGREGATE_FILE = "aggregate.csv"
def get_api_tokens(filename: str):
    try:
        with open(filename, "r") as f:
            text = f.readlines()
        def split_strip(text: str, token: str):
            return text.split(token)[-1].strip()
        token = ": "
        key_dict = {}
        key_dict["bearer_token"] = split_strip(text[0], token)
        key_dict["access_token"] = split_strip(text[1], token)
        key_dict["access_token_secret"] = split_strip(text[2], token)
        key_dict["consumer_key"] = split_strip(text[3], token)
        key_dict["consumer_secret"] = split_strip(text[4], token)
        return key_dict
    except Exception as e:
        print(f"{e}: unable to retrieve api tokens")
        
def get_tweets_by_queries(queries: dict):
    try:
        tweets = []
        for query in queries:
            tweets.append(client.search_recent_tweets(queries[query], max_results=100).data)
        return tweets
    except Exception as e:
        print(e)

def get_candidate_sentiment(tweets: list):
    pos_sentiment = [0] * len(queries)
    neg_sentiment = [0] * len(queries)
    for i, candidate_tweets in enumerate(tweets):
        if candidate_tweets is None:
            pos_sentiment[i] = 0
            neg_sentiment[i] = 0
            continue
        pos_tweets = 0
        for tweet in candidate_tweets:
            if analysis.analyze(str(tweet)).lower() == 'positive':
                pos_tweets += 1
        pos_sentiment[i] = pos_tweets
        neg_sentiment[i] = len(candidate_tweets) - pos_tweets
    return (pos_sentiment, neg_sentiment)

def plot_data(pos_sentiment: list, neg_sentiment: list) -> None:
    fig = plt.figure(figsize= (6,5))
    candidates = ["Peter Obi", "Bola Ahmed Tinibu", "Atiku Abubakar", "Rabiu Kwankwaso"]
    total_tweets = np.array(pos_sentiment) + np.array(neg_sentiment)
    pos_percent = np.array(pos_sentiment)/ total_tweets * 100
    neg_percent = np.array(neg_sentiment)/ total_tweets * 100
    position = np.array(range(1, len(total_tweets) + 1))
    width = 0.3
    plt.bar(position, pos_percent, width=width, color="green", align="center", label="positive sentiment")
    plt.bar(position + width, neg_percent, width=width, color="red", align="center", label="negative sentiment")
    plt.xticks((position + position + width)/2 , candidates)
    plt.legend()
    plt.tight_layout()
    plt.title("Sentiment for Each Candidate")
    plt.show()

def show_aggregate(filename:str, key: str):
    candidates_data = pd.read_csv(filename)
    try:
        requested_df = candidates_data[key].dropna()
    except KeyError:
        print(f'Key {key} does not exist. Options ["PO", "BAT", "AA", "RK"]')
    else:
        keys = {"PO": "Peter Obi", "BAT": "Bola Ahmed Tinibu", "AA": "Atiku Abubakar", 'RK': "Rabiu Kwankwaso"}
        title = f"CHANGE IN PUBLIC SENTIMENT OF {keys[key].upper()} OVER TIME"
        pos_percent = []
        neg_percent = []
        for split_data in requested_df.str.split("|"):
            pos_percent.append(float(split_data[0]))
            neg_percent.append(float(split_data[-1]))
        plt.plot(pos_percent, color="green", label="Positive")
        plt.plot(neg_percent, color="red", label="Negative")
        plt.legend()
        plt.title(title)
        plt.show()

def add_to_csv(filename: str, pos: list, neg: list):
    def merge(pos: int, neg: int):
        total = pos + neg
        return str(pos * 100/total) + "|" + str(neg * 100/total)

    data = [merge(*info) for info in zip(pos, neg)]
    with open(filename, 'a') as f:
        f.write(",".join(data))
        f.write("\n")

if __name__ == "__main__":
    queries = {
        "Peter Obi": """Peter Obi
                        -Bola -Ahmed -Tinibu -@officialBAT -from:officialBAT
                        -Atiku -Abubakar -@atiku -from:atiku
                        -Kwankwaso -Rabiu -@KwankwasoRM -from:KwankwasoRM
                        -from:PeterObi -is:retweet""",
                        
        "Bola Ahmed Tinibu": """Tinibu
                                -Peter -Obi -@PeterObi -from:PeterObi
                                -Atiku -Abubakar -@atiku -from:atiku
                                -Kwankwaso -Rabiu -@KwankwasoRM -from:KwankwasoRM
                                -from:officialBAT -is:retweet""",

        "Atiku Abubakar": """Atiku
                            -Bola -Ahmed -Tinibu -@officialBAT -from:officialBAT
                            -Peter -Obi -@PeterObi -from:PeterObi
                            -Kwankwaso -Rabiu -@KwankwasoRM -from:KwankwasoRM
                            -from:atiku  -is:retweet""",
        
        "Rabiu Kwankwaso": """Kwankwaso
                            -Bola -Ahmed -Tinibu -@officialBAT -from:officialBAT
                            -Peter -Obi -@PeterObi -from:PeterObi
                            -Atiku -Abubakar -@atiku -from:atiku
                            -from:KwankwasoRM  -is:retweet"""
    }

    
    client = tweepy.Client(**get_api_tokens("../key.txt"))
    tweets = get_tweets_by_queries(queries)
    total_pos_sentiment_per_candidate, total_neg_sentiment_per_candidate = get_candidate_sentiment(tweets)
    add_to_csv(AGGREGATE_FILE, total_pos_sentiment_per_candidate, total_neg_sentiment_per_candidate)
    plot_data(total_pos_sentiment_per_candidate, total_neg_sentiment_per_candidate)
    show_aggregate(AGGREGATE_FILE, "BAT")
    show_aggregate(AGGREGATE_FILE, "PO")
    show_aggregate(AGGREGATE_FILE, "AA")
    show_aggregate(AGGREGATE_FILE, "RK")