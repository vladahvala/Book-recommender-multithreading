# Memento

class SearchMemento:
    """
    Клас для збереження стану пошуку (Memento).

    .. note::
       Цей клас є частиною паттерну **Memento**, який дозволяє зберігати і відновлювати стан об'єкта.
    """
    def __init__(self, query, group_mode, show_date, show_rating):
        self.query = query
        self.group_mode = group_mode
        self.show_date = show_date
        self.show_rating = show_rating

class SearchHistory:
    """
    Менеджер історії станів пошуку для реалізації Undo/Redo.

    .. note::
       Цей клас реалізує логіку збереження, відновлення та переміщення між станами,
       що є ключовою частиною паттерну **Memento**.
    """
    def __init__(self):
        self.history = []
        self.future = []

    def save(self, memento):
        """
        Зберігає новий стан пошуку.

        .. note::
           При збереженні нового стану скидається "майбутнє" (redo) історії.
        """
        self.history.append(memento)
        self.future.clear()  # після нового пошуку "вперед" недоступний

    def undo(self):
        """
        Повертається до попереднього стану.

        .. note::
           Використовується для реалізації функції Undo у паттерні **Memento**.
        """
        if len(self.history) < 2:
            return None
        self.future.append(self.history.pop())
        return self.history[-1]

    def redo(self):
        """
        Переходить до наступного збереженого стану, якщо він існує.

        .. note::
           Використовується для реалізації функції Redo у паттерні **Memento**.
        """
        if self.future:
            memento = self.future.pop()
            self.history.append(memento)
            return memento
        return None