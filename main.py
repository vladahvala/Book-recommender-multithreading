import sys
import requests
from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QScrollArea, QComboBox
)

from book_components import BookComposite, BookLeaf  # переконайся, що ці класи коректні
from observer import BookNotifier, UserKeywordSubscriber
from search_memento import SearchMemento, SearchHistory

from concurrent.futures import ThreadPoolExecutor, as_completed

import time

from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QEventLoop, QUrl


class WorkerSignals(QObject):
    finished = pyqtSignal(dict, float)
    error = pyqtSignal(str)

class SearchWorker(QRunnable):
    def __init__(self, query, max_results=20):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            start_time = time.perf_counter()
            url = f"https://www.googleapis.com/books/v1/volumes?q={self.query}&maxResults={self.max_results}"
            response = requests.get(url)
            if response.status_code != 200:
                self.signals.error.emit("Error fetching data from Google Books API.")
                return

            data = response.json()
            elapsed = time.perf_counter() - start_time
            self.signals.finished.emit(data, elapsed)

        except Exception as e:
            self.signals.error.emit(str(e))


class BookRecommender(QWidget):
    def __init__(self):
        super().__init__()

        # Створюємо об’єкт BookNotifier і підписника
        self.notifier = BookNotifier()
        self.keyword_subscriber = UserKeywordSubscriber()
        self.notifier.subscribe(self.keyword_subscriber)
        self.history = SearchHistory()


        self.init_ui()

    def init_ui(self):
        self.apply_styles()
        self.setWindowTitle("Book Recommender System")
        self.setGeometry(200, 100, 1250, 900)

        self.layout = QVBoxLayout(self)

        self.heading = QLabel("BOOK RECOMMENDATION", self)
        self.heading.setStyleSheet("font: 30px bold; color: red;")
        self.heading.setAlignment(Qt.AlignCenter)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Enter book name")
        self.search_box.setStyleSheet("font: 20px; background-color: white;")

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search)

        self.check_var = QCheckBox("Publish Date", self)
        self.check_var.setChecked(True)

        self.check_var2 = QCheckBox("Rating", self)
        self.check_var2.setChecked(True)

        self.grouping_box = QComboBox(self)
        self.grouping_box.addItem("No Grouping")
        self.grouping_box.addItem("Group by Year")
        self.grouping_box.addItem("Group by Rating")
        self.grouping_box.addItem("Group by First Letter")
        self.grouping_box.addItem("Group by Author")
        self.grouping_box.currentIndexChanged.connect(self.search)

        # --- Нові елементи для підписки на ключові слова ---
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText("Enter keyword to subscribe")
        self.keyword_input.setStyleSheet("font: 16px; background-color: white;")

        self.subscribe_button = QPushButton("Subscribe Keyword", self)
        self.subscribe_button.clicked.connect(self.add_keyword_subscription)

        self.keywords_label = QLabel("Subscribed keywords: None", self)
        self.keywords_label.setStyleSheet("color: blue; font: 14px;")
        # -------------------------------------------------------

        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.check_var)
        self.layout.addWidget(self.check_var2)
        self.layout.addWidget(QLabel("Group by:", self))
        self.layout.addWidget(self.grouping_box)

        # Кнопки Undo і Redo
        self.undo_button = QPushButton("Undo", self)
        self.undo_button.clicked.connect(self.undo_search)

        self.redo_button = QPushButton("Redo", self)
        self.redo_button.clicked.connect(self.redo_search)

        self.undo_button.setObjectName("undoButton")
        self.redo_button.setObjectName("redoButton")

        self.layout.addWidget(self.undo_button)
        self.layout.addWidget(self.redo_button)


        # Додаємо нові елементи для підписки
        self.layout.addWidget(self.keyword_input)
        self.layout.addWidget(self.subscribe_button)
        self.layout.addWidget(self.keywords_label)

        self.results_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_widget.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_widget)
        self.layout.addWidget(self.scroll_area)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
                font-size: 16px;
            }
            QLabel#heading {
                font-size: 30px;
                font-weight: bold;
                color: #B22222;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fdfdfd;
            }
            QPushButton {
                padding: 6px 12px;
                font-weight: bold;
                background-color: #007ACC;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
            QCheckBox {
                margin: 5px;
            }
            QComboBox {
                padding: 6px;
                border-radius: 5px;
            }
            QLabel#keywords {
                color: #003399;
                font-style: italic;
            }
            QScrollArea {
                background-color: #FAFAFA;
                border: none;
            }
                           
            QPushButton#undoButton {
                background-color: #FF6F61;  /* теплий червоний/помаранчевий */
                color: white;
            }

            QPushButton#undoButton:hover {
                background-color: #E85C50;
            }

            QPushButton#redoButton {
                background-color: #4CAF50;  /* зелений */
                color: white;
            }

            QPushButton#redoButton:hover {
                background-color: #3E8E41;
            }

        """)

    def add_keyword_subscription(self):
        keyword = self.keyword_input.text().strip().lower()
        if keyword:
            self.keyword_subscriber.add_keyword(keyword)
            keywords_list = ', '.join(sorted(self.keyword_subscriber.keywords))
            self.keywords_label.setText(f"Subscribed keywords: {keywords_list}")
            self.keyword_input.clear()


    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def save_current_state_as_memento(self):
        memento = SearchMemento(
            query=self.search_box.text().strip(),
            group_mode=self.grouping_box.currentText(),
            show_date=self.check_var.isChecked(),
            show_rating=self.check_var2.isChecked()
        )
        self.history.save(memento)


    def restore_search_from_memento(self, memento):
        self.search_box.setText(memento.query)
        index = self.grouping_box.findText(memento.group_mode)
        if index != -1:
            self.grouping_box.setCurrentIndex(index)
        self.check_var.setChecked(memento.show_date)
        self.check_var2.setChecked(memento.show_rating)
        self.perform_search_from_memento(memento)

    def perform_search_from_memento(self, memento):
        self.clear_results()

        if not memento.query:
            return

        # Функція для обробки результатів пошуку, як on_results_ready
        def handle_results(data):
            group_mode = memento.group_mode
            grouped = {}
            ungrouped = []

            for item in data.get('items', []):
                info = item.get('volumeInfo', {})
                title = info.get('title', 'N/A')
                published_date = info.get('publishedDate', 'N/A')
                rating = info.get('averageRating', 'N/A')
                image = info.get('imageLinks', {}).get('thumbnail', '')
                authors = info.get('authors', [])

                self.notifier.notify(title)
                leaf = BookLeaf(title, image, published_date, rating, authors)

                if group_mode == "Group by Year":
                    key = published_date.split('-')[0] if published_date != 'N/A' else "Unknown"
                elif group_mode == "Group by Rating":
                    key = str(rating) if rating != 'N/A' else "No Rating"
                elif group_mode == "Group by First Letter":
                    key = title[0].upper() if title and title[0].isalpha() else "#"
                elif group_mode == "Group by Author":
                    key = authors[0] if authors else "Unknown Author"
                else:
                    key = None

                if key is None:
                    ungrouped.append(leaf)
                else:
                    if key not in grouped:
                        grouped[key] = BookComposite(key)
                    grouped[key].add(leaf)

            if group_mode == "No Grouping":
                for leaf in ungrouped:
                    leaf.display(self.results_layout, show_date=memento.show_date, show_rating=memento.show_rating)
            else:
                for key in sorted(grouped.keys()):
                    grouped[key].display(self.results_layout, show_date=memento.show_date, show_rating=memento.show_rating)

        # Запускаємо асинхронний пошук через SearchWorker
        worker = SearchWorker(memento.query)
        
        # Підписуємося на сигнал, щоб отримати результати і передати в handle_results
        worker.results_ready.connect(handle_results)
        
        # Запускаємо воркер у пулі потоків
        self.threadpool.start(worker)


    def undo_search(self):
        memento = self.history.undo()
        if memento:
            self.restore_search_from_memento(memento)

    def redo_search(self):
        memento = self.history.redo()
        if memento:
            self.restore_search_from_memento(memento)


    def search(self):
        self.save_current_state_as_memento()
        self.clear_results()
        query = self.search_box.text().strip()
        if not query:
            return

        self.thread_pool = QThreadPool.globalInstance()
        worker = SearchWorker(query)

        worker.signals.finished.connect(self.handle_search_results)
        worker.signals.error.connect(self.handle_search_error)

        self.thread_pool.start(worker)

    def handle_search_results(self, data, elapsed):
        group_mode = self.grouping_box.currentText()
        grouped = {}
        ungrouped = []

        start_grouping = time.perf_counter()  # починаємо вимірювати час групування

        for item in data.get('items', []):
            info = item.get('volumeInfo', {})
            title = info.get('title', 'N/A')
            published_date = info.get('publishedDate', 'N/A')
            rating = info.get('averageRating', 'N/A')
            image = info.get('imageLinks', {}).get('thumbnail', '')
            authors = info.get('authors', [])

            self.notifier.notify(title)

            leaf = BookLeaf(title, image, published_date, rating, authors)

            if group_mode == "Group by Year":
                key = published_date.split('-')[0] if published_date != 'N/A' else "Unknown"
            elif group_mode == "Group by Rating":
                key = str(rating) if rating != 'N/A' else "No Rating"
            elif group_mode == "Group by First Letter":
                key = title[0].upper() if title and title[0].isalpha() else "#"
            elif group_mode == "Group by Author":
                key = authors[0] if authors else "Unknown Author"
            else:
                key = None

            if key is None:
                ungrouped.append(leaf)
            else:
                if key not in grouped:
                    grouped[key] = BookComposite(key)
                grouped[key].add(leaf)

        end_grouping = time.perf_counter()  # кінець вимірювання часу групування
        grouping_time = end_grouping - start_grouping
        print(f"Grouping took {grouping_time:.4f} seconds")

        if group_mode == "No Grouping":
            for leaf in ungrouped:
                leaf.display(
                    self.results_layout,
                    show_date=self.check_var.isChecked(),
                    show_rating=self.check_var2.isChecked()
                )
        else:
            for key in sorted(grouped.keys()):
                grouped[key].display(
                    self.results_layout,
                    show_date=self.check_var.isChecked(),
                    show_rating=self.check_var2.isChecked()
                )



    def handle_search_error(self, message):
        QMessageBox.critical(self, "Помилка пошуку", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BookRecommender()
    window.show()
    
    sys.exit(app.exec_())
