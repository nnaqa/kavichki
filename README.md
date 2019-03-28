# kavichki

Тестовое задание:
Вам предлагается развернуть на сервере или локально любую из выбранных вами БД (но предлагаю выбрать что-то более современное).
При помощи браузера Google Chrome под управлением Selenium, собрать данные из таблицы,
  находящейся тут http://tereshkova.test.kavichki.com в вашу таблицу на сервере, распарсив данные.
Далее заполнить некоторыми данными таблицу на сайте «Терешкова», сравнить ее результаты с вашей БД и с теми данными,
  которые вы на самом деле вводили и вывести результат об изменениях.
+ можно несколько функциональных UI тестов на ваше усмотрение по этой таблице на сайте.
Код желательно написать на Python.

Реализация и техническая информация:
Выбранная БД - PostgreSQL 11
Версия Python - 3.6.3
Версия Goggle - 72.0.3626.121

Чтобы воспроизвести запуск теста, необходимо установить БД PostgreSQL и указать авторизационные данные в файле database.ini
Основной файл с тестом: main_test.py

Реализовано 6 тестов, из которых 3 упадут в ошибку. Ошибки ожидаемы, в логе будут комментарии.

Пример вывода в консоль: log_example.txt
