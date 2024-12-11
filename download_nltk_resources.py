import nltk

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Optional: Verify the download
from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
test_sentence = "This is an amazing product!"
sentiment = analyzer.polarity_scores(test_sentence)
print(f"Sentiment Analysis for '{test_sentence}': {sentiment}")
