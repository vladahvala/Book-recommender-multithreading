# Memento

class SearchMemento:
    def __init__(self, query, group_mode, show_date, show_rating):
        self.query = query
        self.group_mode = group_mode
        self.show_date = show_date
        self.show_rating = show_rating

class SearchHistory:
    def __init__(self):
        self.history = []
        self.future = []

    def save(self, memento):
        self.history.append(memento)
        self.future.clear()  # після нового пошуку "вперед" недоступний

    def undo(self):
        if len(self.history) < 2:
            return None
        self.future.append(self.history.pop())
        return self.history[-1]

    def redo(self):
        if self.future:
            memento = self.future.pop()
            self.history.append(memento)
            return memento
        return None