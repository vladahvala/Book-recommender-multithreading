# Оbserver

class Observer:
    def update(self, book):
        pass

class BookNotifier:
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def notify(self, book):
        for observer in self.observers:
            observer.update(book)


class UserKeywordSubscriber(Observer):
    def __init__(self):
        self.keywords = set()

    def add_keyword(self, keyword):
        self.keywords.add(keyword.lower())

    def update(self, book_title):
        for keyword in self.keywords:
            if keyword in book_title.lower():
                print(f"📢 Found book with '{keyword}': {book_title}")
