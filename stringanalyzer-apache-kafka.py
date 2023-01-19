# Reminder! You will have to set up the kafka consumer and configure it to consume data from the correct topic before you can start getting data from kafka.

from collections import Counter
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import FreqDist
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from storm import Spout, emit, log
import nltk

nltk.download("stopwords")

class KafkaSpout(Spout):
    def initialize(self, stormconf, context):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words("english"))

    def nextTuple(self):
        # Get data from Kafka
        
          # The poll() method takes a timeout value as an argument, 
          # which is the time in seconds to wait for new data to arrive. 
          # In this example, the timeout value is set to 1 second.
        data = self.kafka_consumer.poll(1.0)
        words = word_tokenize(data)
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        word_count = len(filtered_words)
        letter_count = Counter(c for c in data if c.isalpha())
        most_common_letter = letter_count.most_common(1)[0][0]
        punctuation_count = Counter(c for c in data if not c.isalpha())
        most_common_word = Counter(filtered_words).most_common(1)[0][0]
        sentiment = self.sentiment_analyzer.polarity_scores(data)
        fdist = nltk.FreqDist(filtered_words)
        wordcloud = WordCloud().generate_from_frequencies(fdist)
        wordcloud.to_file("wordcloud.png")

        # Emit the results
        emit([word_count, letter_count, most_common_letter, punctuation_count, most_common_word, sentiment, fdist])
