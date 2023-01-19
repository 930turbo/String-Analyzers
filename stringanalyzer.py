import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
from collections import Counter
from nltk.corpus import stopwords
from wordcloud import WordCloud

nltk.download("stopwords")

data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# Count the number of words in the string
stop_words = set(stopwords.words("english"))
words = nltk.word_tokenize(data)
filtered_words = [word for word in words if word.lower() not in stop_words]
word_count = len(filtered_words)
print("Word count: ", word_count)

# Count the number of occurrences of each letter
letter_count = Counter(c for c in data if c.isalpha())
print("Letter count: ", letter_count)

# Find the most common letter
most_common_letter = letter_count.most_common(1)[0][0]
print("Most common letter: ", most_common_letter)

# Count the number of occurrences of each punctuation mark
punctuation_count = Counter(c for c in data if not c.isalpha())
print("Punctuation count: ", punctuation_count)

# Identifying the most common word
word_count = Counter(filtered_words)
most_common_word = word_count.most_common(1)[0][0]
print("Most common word: ", most_common_word)

# Analyzing the sentiment of the data
from nltk.sentiment import SentimentIntensityAnalyzer

sentiment_analyzer = SentimentIntensityAnalyzer()
sentiment = sentiment_analyzer.polarity_scores(data)
print("Sentiment of the data: ", sentiment)

# Creating a frequency distribution
from nltk import FreqDist

fdist = FreqDist(filtered_words)
print("Frequency Distribution: ", fdist)

# Creating a wordcloud
wordcloud = WordCloud().generate_from_frequencies(fdist)

wordcloud.to_file("wordcloud.png")

# Saving the results in a file
with open("output.txt", "w") as f:
    f.write("Word count: " + str(word_count) + "\n")
    f.write("Letter count: " + str(letter_count) + "\n")
    f.write("Most common letter: " + most_common_letter + "\n")
    f.write("Punctuation count: " + str(punctuation_count) + "\n")
    f.write("Most common word: " + most_common_word + "\n")
    f.write("Sentiment of the data: " + str(sentiment) + "\n")
    f.write("Frequency Distribution: " + str(fdist))
