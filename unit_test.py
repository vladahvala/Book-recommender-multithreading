import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
import sys

from main import BookRecommender 

app = QApplication(sys.argv)  # QApplication має бути 1 раз на сесію

from observer import BookNotifier, UserKeywordSubscriber
from book_components import BookComposite, BookLeaf  


#--------------------------------------------------------------------
# Покрито юніт-тестами:
# 1. BookComposite:
#    - додавання книжок у композит;
#    - правильне відображення книжок і заголовка в layout після виклику display().
#
# 2. Observer Pattern:
#    - оповіщення спостерігача, якщо в назві книги є додане ключове слово;
#    - відсутність оповіщення, якщо ключове слово не знайдено.
#
# 3. BookRecommender:
#    - додавання ключових слів до підписки (з переведенням у нижній регістр);
#    - ігнорування дубльованих ключових слів;
#    - обробка пошуку з моканим API-відповіддю (requests.get);
#    - збереження, відновлення та перевірка станів (Memento: undo/redo);
#    - правильне відновлення стану інтерфейсу з memento-об'єкта.
#--------------------------------------------------------------------


class TestBookComposite(unittest.TestCase):
    def setUp(self):
        # Створюємо кілька книжок (листків)
        self.book1 = BookLeaf("Book One", "", "2020-01-01", 4.5, ["Author A"])
        self.book2 = BookLeaf("Book Two", "", "2019-05-20", 3.8, ["Author B"])

        # Створюємо композит (групу книжок)
        self.group = BookComposite("My Book Group")

        # Створюємо контейнер для відображення (імітація layout)
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

    def test_add_and_count_children(self):
        self.group.add(self.book1)
        self.group.add(self.book2)
        self.assertEqual(len(self.group.children), 2)

    def test_display_adds_widgets(self):
        self.group.add(self.book1)
        self.group.add(self.book2)

        # Перед викликом display у layout має бути 0 віджетів
        self.assertEqual(self.layout.count(), 0)

        # Викликаємо display - має додатися заголовок і дві книжки
        self.group.display(self.layout, show_date=True, show_rating=True)

        # Тепер у layout має бути щонайменше 3 віджети (заголовок + 2 книжки)
        self.assertTrue(self.layout.count() >= 3)


class TestObserverPattern(unittest.TestCase):

    @patch("builtins.print")
    def test_observer_notified_on_keyword_addition(self, mock_print):
        # Arrange
        notifier = BookNotifier()
        subscriber = UserKeywordSubscriber()
        notifier.subscribe(subscriber)

        # Додаємо ключове слово
        subscriber.add_keyword("python")

        # Act — надсилаємо повідомлення з назвою книги
        notifier.notify("Learning Python the Hard Way")

        # Assert — перевіряємо, що print було викликано з відповідним повідомленням
        mock_print.assert_called_with("📢 Found book with 'python': Learning Python the Hard Way")

    @patch("builtins.print")
    def test_observer_not_notified_if_keyword_absent(self, mock_print):
        notifier = BookNotifier()
        subscriber = UserKeywordSubscriber()
        notifier.subscribe(subscriber)

        subscriber.add_keyword("java")
        notifier.notify("C++ Primer")

        mock_print.assert_not_called()



class TestBookRecommender(unittest.TestCase):
    def setUp(self):
        self.window = BookRecommender()

    def test_add_keyword_subscription(self):
        self.window.keyword_input.setText("Python")
        self.window.add_keyword_subscription()

        # Перевіряємо ключове слово у нижньому регістрі
        self.assertIn("python", self.window.keyword_subscriber.keywords)
        self.assertEqual(self.window.keywords_label.text(), "Subscribed keywords: python")
        self.assertEqual(self.window.keyword_input.text(), "")


    @patch('requests.get')
    def test_search_with_mocked_response(self, mock_get):
        # Підготовка мок-даних як відповідь API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Test Book",
                        "publishedDate": "2020-01-01",
                        "averageRating": 4.5,
                        "imageLinks": {"thumbnail": "http://image.url"},
                        "authors": ["Author One"]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        self.window.search_box.setText("Test")
        self.window.grouping_box.setCurrentText("No Grouping")
        self.window.search()

        # Переконуємось, що результати відображені (в лейаутах є віджети)
        self.assertTrue(self.window.results_layout.count() > 0)

    def test_save_and_restore_memento(self):
        # Спочатку встановлюємо стан у вікні
        self.window.search_box.setText("Python")
        self.window.grouping_box.setCurrentText("Group by Year")
        self.window.check_var.setChecked(True)       # show_date
        self.window.check_var2.setChecked(False)     # show_rating

        # Зберігаємо цей стан
        self.window.save_current_state_as_memento()

        # Виконуємо undo — має повернути цей останній стан
        memento_undo = self.window.history.undo()
        self.assertIsNotNone(memento_undo)

        # Виконуємо redo — відновлюємо цей же стан
        memento_redo = self.window.history.redo()
        self.assertIsNotNone(memento_redo)

        # Перевіряємо значення збереженого стану
        self.assertEqual(memento_redo.query, "Python")
        self.assertEqual(memento_redo.group_mode, "Group by Year")
        self.assertTrue(memento_redo.show_date)
        self.assertEqual(memento_redo.show_rating, self.window.check_var2.isChecked())

        # Відновлюємо інтерфейс із мему
        self.window.restore_search_from_memento(memento_redo)

        # Перевіряємо, що інтерфейс відновлено коректно
        self.assertEqual(self.window.search_box.text(), "Python")
        self.assertEqual(self.window.grouping_box.currentText(), "Group by Year")
        self.assertTrue(self.window.check_var.isChecked())
        self.assertEqual(self.window.check_var2.isChecked(), memento_redo.show_rating)

    def test_add_duplicate_keyword_ignored(self):
        self.window.keyword_input.setText("Python")
        self.window.add_keyword_subscription()

        self.window.keyword_input.setText("Python")  # Спроба додати дублікат
        self.window.add_keyword_subscription()

        self.assertEqual(len(self.window.keyword_subscriber.keywords), 1)
        self.assertEqual(self.window.keywords_label.text(), "Subscribed keywords: python")


if __name__ == '__main__':
    unittest.main()
