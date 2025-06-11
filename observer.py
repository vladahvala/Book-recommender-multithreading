# Оbserver

class Observer:
    def update(self, book):
        """
        Метод, який викликається при оновленні.

        .. note::
           Це частина паттерну **Observer** — інтерфейс спостерігача.
        """
        pass

class BookNotifier:
    """
        Ініціалізує список спостерігачів.

        .. note::
           Цей клас є суб'єктом (Subject) у паттерні **Observer**.
    """
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        """
        Додає нового спостерігача.

        .. note::
           Метод підписки у паттерні **Observer**.
        """
        self.observers.append(observer)

    def notify(self, book):
        """
        Повідомляє усіх підписаних спостерігачів про подію.

        .. note::
           Метод сповіщення у паттерні **Observer**.
        """
        for observer in self.observers:
            observer.update(book)


class UserKeywordSubscriber(Observer):
    """
        Ініціалізує набір ключових слів для спостереження.

        .. note::
           Конкретний спостерігач у паттерні **Observer**.
    """
    def __init__(self):
        self.keywords = set()

    def add_keyword(self, keyword):
        """
        Додає ключове слово для пошуку.

        .. note::
           Внутрішня логіка спостерігача (Observer).
        """
        self.keywords.add(keyword.lower())

    def update(self, book_title):
        """
        Оновлює інформацію про книгу, якщо знайдено ключове слово.

        .. note::
           Перевизначення методу update в паттерні **Observer**.
        """
        for keyword in self.keywords:
            if keyword in book_title.lower():
                print(f"📢 Found book with '{keyword}': {book_title}")
