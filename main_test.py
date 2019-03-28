# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

import DB as db


def get_column_names(driver):
    ''' Получение всех наименований столбцов таблицы списком '''
    table_headers = driver.find_element_by_xpath('//*[@id="tbl"]/thead')
    cols = table_headers.find_elements(By.TAG_NAME, 'th')
    return [th.text.replace(' ', '_').replace('.', '').replace(',', '') for th in cols]

def get_create_table_sql(driver):
    ''' Формирование sql на создание таблицы '''
    column_names = get_column_names(driver)
    column_names_to_sql = ''
    for name in column_names:
        column_names_to_sql += name + ' VARCHAR (50) NOT NULL, '
    column_names_to_sql = column_names_to_sql[:-2]
    # sql для создания таблицы
    return 'CREATE TABLE main_test (' + column_names_to_sql + ');'

def get_all_rows(driver):
    ''' Получение всех значений в теле таблицы построчно '''
    table_body = driver.find_element_by_xpath('//*[@id="tbl"]/tbody')
    rows = table_body.find_elements(By.TAG_NAME, 'tr')
    rows_list = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        rows_list.append([td.text for td in cols])
    return rows_list

def delete_old_table(cur):
    ''' Удаление таблицы, если существовала ранее '''
    cur.execute("SELECT to_regclass('main_test');")  # возвращает название таблицы, если она существует
    if cur.fetchone()[0]:  # если не None
        cur.execute('DROP TABLE main_test;')
        print('Previous main_test table has been deleted')

def compare_two_lists_value(list_1, list_2, column_names, element_number):
    ''' Проверка совпадения значений '''
    if list_1[element_number] == list_2[element_number]:
        print(column_names[element_number] + ' - значения совпадают')
    else:
        print(column_names[element_number] + ' - значения не совпадают')


driver = webdriver.Chrome()     # инициализация браузера

cur, conn = db.connect()                                # создание соединения к БД
driver.get('http://tereshkova.test.kavichki.com/')      # открытие страницы
driver.implicitly_wait(10)

delete_old_table(cur)                                   # удаление старой таблицы
cur.execute(get_create_table_sql(driver))               # создание новой таблицы
# заполнение таблицы
rows_list = get_all_rows(driver)  # все значения таблицы
for row in rows_list:
    cur.execute('INSERT INTO main_test VALUES (' + str(row)[1:-1] + '); ')


class TestMain(unittest.TestCase):
    ''' Страница "Список покупок" '''
    new_row_text = ['Гантели черные', '2', '500', 'Удалить']

    def setUp(self):
        pass

    def test_0_check_header(self):
        ''' Проверка заголовка страницы '''
        header_text = driver.find_element_by_id('header')
        assert header_text.text == 'Список покупок'

    def test_1_add_new_row(self):
        ''' Добавление новых данных в таблицу '''
        rows_count_before = len(get_all_rows(driver))
        driver.find_element_by_id('open').click()
        driver.find_element_by_id('name').send_keys(self.new_row_text[0])
        driver.find_element_by_id('count').send_keys(self.new_row_text[1])
        driver.find_element_by_id('price').send_keys(self.new_row_text[2])
        driver.find_element_by_id('add').click()

        rows_count_after = len(get_all_rows(driver))
        rows_count_diff = rows_count_after - rows_count_before
        if rows_count_diff > 1:
            self.fail('В таблицу занесено ' + str(rows_count_diff) + ' строк. Ожидалась 1 строка')
        elif rows_count_diff != 1:
            self.fail('В таблицу не занесено ни одной строки. Ожидалась 1 строка')
        assert rows_count_after > rows_count_before and rows_count_diff == 1

    def test_2_compare_new_row_with_db(self):
        ''' Сравнение новых данных с данными в БД '''
        cur.execute('SELECT * FROM main_test')
        all_rows_from_db = [list(i) for i in cur.fetchall()]
        assert self.new_row_text not in all_rows_from_db

    def test_3_check_new_row_contains(self):
        ''' Проверка корректности занесения новых данных
                Тест упадет, т.к. присутствует баг:
                Поля Количество и стоимость поменяны местами
        '''
        new_row_text = self.new_row_text                    # введенные тестовые данные
        column_names = get_column_names(driver)             # наименования столбцов
        added_new_row_text = get_all_rows(driver)[-1:][0]   # фактически добавленная строка
        print()

        # проверка совпадения значений
        for i in range(len(new_row_text)):
            compare_two_lists_value(new_row_text, added_new_row_text, column_names, i)
        if new_row_text in get_all_rows(driver)[-1:][0]:
            print('Новая строка занесена корректно')
        else:
            self.fail('Новая строка занесена не корректно')
        assert new_row_text in get_all_rows(driver)[-1:][0]

    def test_4_check_reset_lnk(self):
        ''' Проверка функционала для ссылки "Сбросить" '''
        reset_lnk = driver.find_element_by_partial_link_text('Сбросить')
        name_field = driver.find_element_by_id('name')
        if not name_field.is_displayed():
            driver.find_element_by_id('open').click()
            driver.find_element_by_id('name').send_keys(self.new_row_text[0])
            driver.find_element_by_id('count').send_keys(self.new_row_text[1])
            driver.find_element_by_id('price').send_keys(self.new_row_text[2])
            driver.find_element_by_id('add').click()
        if name_field.get_attribute('value') != '':
            reset_lnk.click()
        if name_field.get_attribute('value') != '':
            self.fail('Ссылка Сбросить не работает - введенные данные не удалены')
        assert name_field.get_attribute('value') == ''

    def test_5_compare_new_row_with_db(self):
        ''' Проверка того, что введенные данные присутстуют в таблице после перезагрузки страницы '''
        driver.refresh()
        all_existing_rows = get_all_rows(driver)
        if len(all_existing_rows) == 4:
            self.fail('Новая строка не сохранена. После обновления страницы - введенные данные отсутствуют.')
        assert self.new_row_text in all_existing_rows and len(all_existing_rows) > 4


    def tearDown(self):
        pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMain)
    unittest.TextTestRunner(verbosity=2).run(suite)

driver.close()
db.teardown(conn)