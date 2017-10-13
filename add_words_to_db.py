import sys
import string

from datetime import datetime

import mongoengine

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_etexts
from gutenberg.query import get_metadata

import model

if __name__ == '__main__':

    min_word_length = 4

    do_words = int(sys.argv[1])
    do_books = int(sys.argv[2])
    do_passages = int(sys.argv[3])

    if(do_words):
        print "Loading words..."
        tstart = datetime.now()

        model.Word.objects.delete()

        with open('words.txt', 'r') as f:
            words = []
            for line in f:
                line = line.strip().lower()
                if(len(line) >= min_word_length):
                    words.append(line)

        for word in words:
            word_object = model.Word(word=word).save()

        tend = datetime.now()
        print "Loaded words: Total time: " + str((tend-tstart).seconds)

    if(do_books):
        print "Loading books..."
        tstart = datetime.now()

        model.Book.objects.delete()

        with open('books.txt', 'r') as f:
            books = []
            for line in f:
                books.append(int(line.rstrip()))

        for book in books:
            text = strip_headers(load_etext(book)).strip()
            title = next(iter(get_metadata('title', book)))
            author = next(iter(get_metadata('author', book)))
            book_object = model.Book(text=text, title=title, author=author).save()

        tend = datetime.now()
        print "Loaded books: Total time: " + str((tend-tstart).seconds)

    if(do_passages):

        print "Constructing passages..."
        tstart = datetime.now()

        punctuation_droplist = string.punctuation.replace("-", "")

        model.Passage.objects.delete()

        for book_object in model.Book.objects():
            text = book_object.text

            paragraphs = text.split('\r\n\r\n')
            for paragraph_index, paragraph in enumerate(paragraphs):
                paragraph = paragraph.replace('\r\n', ' ')
                passage_object = model.Passage(book=book_object, paragraph_index=paragraph_index).save()
                for word in paragraph.split(' '):
                    word = str(word).translate(None, punctuation_droplist).lower()
                    word_object = model.Word.get_word_object(word)
                    if(word_object is not None):
                        word_object.update(add_to_set__passages=passage_object)

        tend = datetime.now()
        print "Loaded passages: Total time: " + str((tend-tstart).seconds)
