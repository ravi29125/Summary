from PyPDF2 import PdfReader
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

def text_summarizer(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word.lower() not in stop_words]
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in filtered_words]
    word_freq = {}
    for word in stemmed_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence)
        sentence_score = 0
        for word in sentence_words:
            word = stemmer.stem(word)
            if word in word_freq:
                sentence_score += word_freq[word]
        sentence_scores[sentence] = sentence_score
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(top_sentences)
    return summary


def home(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        pdf_path = fs.path(filename)
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        text=text_summarizer(text)
        os.remove(pdf_path)
        return render(request, 'home.html', {'message': text})
    elif request.method == 'POST':
        s=request.POST.get('input_text')
        s=text_summarizer(s)
        return render(request, 'home.html', {'message': s})
    else:
        return render(request, 'home.html')
