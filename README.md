# String-Analyzer

This project is a Python program that analyzes data in string form. The program takes in a data string as input and performs several analysis tasks on it, including counting the number of words, counting the occurrences of each letter, finding the most common letter, counting the occurrences of each punctuation mark, identifying the most common word, analyzing the sentiment of the data, creating a frequency distribution of the words, and creating a wordcloud of the most frequent words.

## Dependencies
These programs require the following dependencies to be installed:

You can install them by running 
``` pip install nltk ```
``` pip install wordcloud ```
``` pip install mysql-connector-python ```

## Input
These programs take in an input, the data string. This string can contain any combination of letters, numbers, and punctuation marks.

## Output
The program returns several outputs:

Word count: the number of words in the data string
Letter count: a dictionary containing the occurrences of each letter in the data string
Most common letter: the letter that occurs the most in the data string
Punctuation count: a dictionary containing the occurrences of each punctuation mark in the data string
Most common word: the word that occurs the most in the data string
Sentiment of the data: a dictionary containing the overall sentiment of the data string as calculated by NLTK's SentimentIntensityAnalyzer
Frequency Distribution: a dictionary containing the frequency of each word in the data string
wordcloud.png: a file that contains the wordcloud of the most frequent words in the data string
output.txt: a file that contains all the outputs of the program

## Additional notes
The program uses NLTK's stopwords to remove common words like "a", "an", "the", etc. from the data string before counting the words and letters.
The program uses NLTK's tokenize function to tokenize the data string into a list of words
The program uses the WordCloud library to create a wordcloud of the most frequent words in the data string.
The program uses the open() function to open a file and write() function to write the results in the file
The program uses the SentimentIntensityAnalyzer to perform sentiment analysis on the data string.
The program uses the nltk.FreqDist() function to create a frequency distribution of the words in the data string
The program uses the Counter from python's collections module to count the occurrences of each letter and punctuation mark
The program uses the most_common() method of Counter to find the most common letter and word.
