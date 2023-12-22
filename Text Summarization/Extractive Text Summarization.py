import bs4 as bs
import urllib.request
import re
import nltk
import heapq

nltk.download('stopwords')

# defining class
class ArticleSummarizer:
    
    # Initializes the ArticleSummarizer with the URL of the article.
    # URL as parameter
    def __init__(self, url):
        self.url = url
        self.text = self.get_text_from_url()
        self.preprocessed_text = self.preprocess_text()

    # Retrieves the text content from the provided URL
    # Using library urllib and bs4 to recive content from the URL
    def get_text_from_url(self):
        source = urllib.request.urlopen(self.url).read()
        soup = bs.BeautifulSoup(source, 'lxml')
        text = " ".join(paragraph.text for paragraph in soup.find_all('p'))
        text = re.sub(r'\[[0-9]*\]', ' ', text) # Returns a match for any digit between
        text = re.sub(r'\s+', ' ', text) # Returns a match for any digit between
        return text

    # Preprocessing text
    def preprocess_text(self):
        pre_text = self.text.lower() #Change into lower text
        pre_text = re.sub(r'’s', '', pre_text)
        pre_text = re.sub(r'\W', ' ', pre_text) #Returns a match where the string DOES NOT contain any word characters
        pre_text = re.sub(r'\d', ' ', pre_text) # Returns a match where the string contains digits
        pre_text = re.sub(r'\s+', ' ', pre_text) #Returns a match where the string contains a white space character
        return pre_text

    # Tokenize the text
    def tokenize_sentences(self):
        return nltk.sent_tokenize(self.text)
    

    # Stop_words and build histogram of word frequencies
    # set stop_word into 'English'
    def build_word_histogram(self):
        # Count the word per word in in preprocessed text
        word2count = {}
        stop_words = set(nltk.corpus.stopwords.words('english'))
        words = nltk.word_tokenize(self.preprocessed_text)
        for word in words:
            if word not in stop_words:
                if word not in word2count.keys():
                    word2count[word] = 1
                else:
                    word2count[word] += 1

        # Converting counts to weights by dividing each count the maximum count
        max_count = max(word2count.values())
        for key in word2count.keys():
            word2count[key] = word2count[key]/max_count
        return word2count

    # Calculates scores for each sentence based on the word frequencies
    def calculate_sentence_scores(self, word2count):
        sentences = self.tokenize_sentences()
        sent2score = {}
        # check if the word present in word2count
        for sentence in sentences:
            for word in nltk.word_tokenize(sentence.lower()):
                if word in word2count.keys():
                    # If the word is present and  sentence length less than 25 word
                    if len(sentence.split(' ')) < 25:
                        if sentence not in sent2score.keys():
                            sent2score[sentence] = word2count[word]
                        else:
                            sent2score[sentence] += word2count[word]

        return sent2score

    # Generates a summary by selecting the top-scoring sentences
    # uses the heapq module to efficiently find the highest-scoring sentences
    # Set the lines in num_sentences
    def generate_summary(self, sent2score, num_sentences=25):
        best_sentences = heapq.nlargest(num_sentences, sent2score, key=sent2score.get)
        return best_sentences

    def summarize_article(self, num_sentences=25):
        word2count = self.build_word_histogram()
        sent2score = self.calculate_sentence_scores(word2count)
        summary = self.generate_summary(sent2score, num_sentences)
        return summary


# Call the function
url = 'https://time.com/6342827/ceo-of-the-year-2023-sam-altman/'
summarizer = ArticleSummarizer(url)
result = summarizer.summarize_article()

print('\n\nSUMMARY :\n\n')

for summary in result:
    print(summary)
