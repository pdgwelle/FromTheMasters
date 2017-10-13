from mongoengine import *
import mongoengine

db = connect('ftm')

class Book(Document):
    text = StringField()
    title = StringField(unique=True)
    author = StringField()

    def get_paragraph(self, paragraph_index):
        paragraphs = self.text.split('\r\n\r\n')
        return paragraphs[paragraph_index].replace('\r\n', ' ')

    def __repr__(self):
        return '<Book - Title: %r Author: %r>' % (self.title, self.author)


class Passage(Document):
    book = ReferenceField(Book)
    paragraph_index = LongField()

    def __repr__(self):
        return '<Passage - Book: %r Paragraph: %r>' % (self.book.title, self.paragraph_index)


class Word(Document):

    @staticmethod
    def get_word_object(word):
        min_word_length = 4
        if(len(word) >= min_word_length):
            word_list = Word.objects(word=word).first()
            if(word_list is not None):
                return word_list
                
    word = StringField()
    passages = ListField(ReferenceField(Passage, reverse_delete_rule=4))

    meta = {'indexes': ['$word', '#word']}

    def __repr__(self):
        return '<Word: %r>' % (self.word)
