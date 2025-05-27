# Composite 

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
from io import BytesIO
import requests
import time

class BookComponent:
    def display(self, layout, show_date=True, show_rating=True):
        pass

class BookLeaf(BookComponent):
    total_load_time = 0
    load_count = 0

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
                import time  # імпортуємо тут, якщо не було глобально
                start = time.perf_counter()
                response = requests.get(self.poster)
                load_time = time.perf_counter() - start

                # накопичуємо час і кількість
                BookLeaf.total_load_time += load_time
                BookLeaf.load_count += 1

                print(f"[Timing] Image for '{self.title}' loaded in {load_time:.4f} sec")

                img = Image.open(BytesIO(response.content))
                img = img.resize((140, 200))
                img = img.convert("RGB")
                qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                frame_layout.addWidget(image_label)
            except Exception as e:
                print(f"Failed to load image for '{self.title}': {e}")

        # Дата
        if show_date:
            date_label = QLabel(f"Date: {self.date}")
            frame_layout.addWidget(date_label)

        # Рейтинг
        if show_rating:
            rating_label = QLabel(f"Rating: {self.rating}")
            frame_layout.addWidget(rating_label)

        layout.addWidget(frame)

    @classmethod
    def print_average_load_time(cls):
        if cls.load_count == 0:
            print("[Timing] No images loaded yet.")
        else:
            avg_time = cls.total_load_time / cls.load_count
            print(f"[Timing] Average image load time: {avg_time:.4f} seconds over {cls.load_count} images")


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
