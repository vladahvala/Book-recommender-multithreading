Design Patterns Used
====================

Memento
-------

Паттерн **Memento** використовується для збереження і відновлення стану пошуку.

- Застосовано у методах:
  - :py:meth:`BookRecommender.save_current_state_as_memento`
  - :py:meth:`BookRecommender.restore_search_from_memento`
- Клас:
  - :class:`SearchMemento`
  - :class:`SearchHistory`

Composite
---------

Паттерн **Composite** використовується для представлення структури об'єктів у вигляді дерева, де окремі об'єкти та їхні композиції обробляються однаково.

- Застосовано у класах:
  - :class:`BookComponent` — базовий клас компонента.
  - :class:`BookLeaf` — листовий компонент (окрема книжка).
  - :class:`BookComposite` — складений компонент (набір книжок або категорія).

Observer
--------

Паттерн **Observer** використовується для сповіщення зацікавлених об'єктів про зміни стану.

- Застосовано у класах:
  - :class:`BookNotifier` — об'єкт, який повідомляє підписників про події.
  - :class:`Observer` — інтерфейс для спостерігачів.
  - :class:`UserKeywordSubscriber` — конкретний спостерігач, що реагує на ключові слова.
- Застосовано у методах:
  - :py:meth:`BookNotifier.subscribe`
  - :py:meth:`BookNotifier.notify`
