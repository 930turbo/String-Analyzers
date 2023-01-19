import mysql.connector
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import FreqDist
nltk.download('punkt')
nltk.download('vader_lexicon')
from collections import Counter
from nltk.corpus import stopwords
from wordcloud import WordCloud

# Initialize SentimentIntensityAnalyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# Connect to the MySQL database
cnx = mysql.connector.connect(user='username', password='password',
                              host='hostname', database='database_name')

# Create a cursor object to execute the query
cursor = cnx.cursor()

# Execute the query to retrieve the data
cursor.execute("SELECT data_field FROM data_table")

# Fetch all the results
results = cursor.fetchall()

# Process each row of the results
for row in results:
    data = row[0]

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
    sentiment = sentiment_analyzer.polarity_scores(data)
    print("Sentiment of the data: ", sentiment)

    # Creating a frequency distribution
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

# Close the cursor and connection
cursor.close()
cnx.close()
