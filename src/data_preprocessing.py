import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from langdetect import detect


class Preprocessor:

    def is_english(self, text):
        try:
            return detect(text) == 'en'
        except:
            return False

    def preprocessing(self, sentence):
        sentence = str(sentence)
        # Removing whitespaces
        sentence = sentence.strip()
        # Lowercasing
        sentence = sentence.lower()
        # Removing numbers
        sentence = ''.join(char for char in sentence if not char.isdigit())
        # Remove Emojis
        sentence = sentence.encode('ascii', 'ignore').decode('ascii')
        # Removing punctuation
        for punctuation in string.punctuation:
            sentence = sentence.replace(punctuation, '')
        # Tokenizing
        tokenized = word_tokenize(sentence)
        # Lemmatizing
        lemmatizer = WordNetLemmatizer()
        lemmatized = [lemmatizer.lemmatize(word) for word in tokenized]
        cleaned_sentence = " ".join(lemmatized)
        return cleaned_sentence




