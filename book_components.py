# Composite 

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
from io import BytesIO
import requests

class BookComponent:
    def display(self, layout, show_date=True, show_rating=True):
        pass

class BookLeaf(BookComponent):
    def __init__(self, title, poster, date, rating, authors=None):
        self.title = title
        self.poster = poster
        self.date = date
        self.rating = rating
        self.authors = authors or []  # список авторів

    def display(self, layout, show_date=True, show_rating=True):
        frame = QFrame()
        frame.setStyleSheet("background-color: white;")
        frame_layout = QVBoxLayout(frame)

        # Заголовок
        title_label = QLabel(self.title)
        frame_layout.addWidget(title_label)

        # Автор(и)
        if self.authors:
            authors_str = ", ".join(self.authors)
            author_label = QLabel(f"Author(s): {authors_str}")
            frame_layout.addWidget(author_label)

        # Зображення
        if self.poster:
            try:
                response = requests.get(self.poster)
                img = Image.open(BytesIO(response.content))
                img = img.resize((140, 200))
                img = img.convert("RGB")
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                frame_layout.addWidget(image_label)
            except:
                pass

        # Дата
        if show_date:
            date_label = QLabel(f"Date: {self.date}")
            frame_layout.addWidget(date_label)

        # Рейтинг
        if show_rating:
            rating_label = QLabel(f"Rating: {self.rating}")
            frame_layout.addWidget(rating_label)

        layout.addWidget(frame)

class BookComposite(BookComponent):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, component):
        self.children.append(component)

    def display(self, layout, show_date=True, show_rating=True):
        heading = QLabel(f"<h3>{self.name}</h3>")
        heading.setStyleSheet("color: darkblue; margin-top: 10px;")
        layout.addWidget(heading)

        for child in self.children:
            child.display(layout, show_date, show_rating)
