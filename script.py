import datetime
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qs

import pytz
from dateutil.relativedelta import relativedelta


def method1(geonameid):
    """
    Первый метод, поиск города по geonameid.
    :return: При нахождении geonameid в БД - возвращает соответсвующую информацию о городе, иначе False.
    """
    if geonameid:
        found_city = []
        for city in DB_RU:
            if city[0] == geonameid[0]:
                found_city = city
                break
        return found_city
    else:
        return False


def method2(page, amount):
    """
    Второй метод, пространственная выборка городов.
    :param page: Страница, которую необходимо отобразить;
    :param amount: Количество городов на странице;
    :return: Список городов на указанной странице.
    """
    return_list = DB_RU[page * amount:page * amount + amount]
    return return_list


def city_selection(city_to_choose):
    """
    Расширенный поиск города для третьего метода, при необходимости выбирая наиболее населенный из найденных.
    :param city_to_choose: Название города на русском языке, который необходимо найти в базе;
    :return: При нахождении города в БД - возвращает информацию о городе, иначе False.
    """
    all_found = []
    for city in DB_RU:
        if city_to_choose in city[3]:
            all_found.append(city)

    if len(all_found) == 0:
        return False
    elif len(all_found) == 1:
        return all_found[0]
    else:
        population = 0
        final_city = all_found[0]

        for city in all_found:
            if int(city[14]) > population:
                population = int(city[14])
                final_city = city

        return final_city


def method3(city1, city2):
    """
    Третий метод - нахождение двух городов с последующим сравнением, какой из них севернее, и разность часовых поясов;
    :param city1: Название первого города на русском языке;
    :param city2: Название второго города на русском языке;
    :return: При успешном нахождении городов - возвращает информацию о первом городе, втором городе,
    какой город севернее, и разность часовых поясов. Иначе False.
    """
    try:
        found_city1 = city_selection(city1[0])
        found_city2 = city_selection(city2[0])

        if found_city1 and found_city2:
            city1_latitude, city2_latitude = found_city1[4], found_city2[4]
            city1_timezone, city2_timezone = found_city1[17], found_city2[17]

            long_check = f"{city1[0]} находится севернее." if city1_latitude > city2_latitude \
                else f"{city2[0]} находится севернее."

            if city1_timezone == city2_timezone:
                timezone_check = f'У городов один часовой пояс - {city1_timezone}'

            else:  # Вычисление разницы часовых поясов двух городов.
                utcnow = pytz.timezone('utc').localize(datetime.datetime.utcnow())
                city1_tz_now = utcnow.astimezone(pytz.timezone(city1_timezone)).replace(tzinfo=None)
                city2_tz_now = utcnow.astimezone(pytz.timezone(city2_timezone)).replace(tzinfo=None)

                offset = relativedelta(city1_tz_now, city2_tz_now)
                timezone_check = f'У городов разный часовой пояс. Разница во времени между городами ' \
                                 f'на данный момент: {offset.hours} '

            return found_city1, found_city2, long_check, timezone_check
        else:
            raise NameError

    except NameError:
        return False


def method4(city_name):
    """
    Четвертый метод - По введенной части названия города на русском языке возвращает подсказку с возможными
    вариантами продолжений.
    :param city_name: Часть названия города;
    :return: Список возможных вариантов продолжений.
    """
    adjusted_names = []
    for city in DB_RU:
        for name in city[3]:
            if city_name in name:
                adjusted_names.append(name)
                break
    return adjusted_names


class HttpGetHandler(BaseHTTPRequestHandler):
    def output_city(self, param_input, city):
        """
        Функция для вывода информации о городе.
        :param param_input: Введеное пользователем значение;
        :param city: Информация о городе, иначе уведомление об ошибке.
        """
        elem_names = ['geonameid', 'name', 'asciiname', 'alternativenames', 'latitude', 'longitude', 'feature class',
                      'feature code', 'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code',
                      'population', 'elevation', 'dem', 'timezone', 'modifiaction date']

        if city:
            self.wfile.write((str(param_input) + '<br>').encode('utf-8'))
            for count, element in enumerate(city):
                if count == 3:
                    alt_names = ', '.join(element)
                    self.wfile.write((str(count) + ' ' + elem_names[count] + ':\t' + alt_names + '<br>').encode('utf-8'))
                    continue

                self.wfile.write((str(count) + ' ' + elem_names[count] + ':\t' + str(element) + '<br>').encode('utf-8'))

            self.wfile.write('______________________________________________<br><br>'.encode('utf-8'))
        else:
            self.wfile.write('Такого города не существует, либо была допущена ошибка в написании.'.encode('utf-8'))

    def do_GET(self):
        method_path = urlparse(self.path).path
        components = parse_qs(urlparse(self.path).query)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('<html><head><meta charset="utf-8"></head></html>'.encode())

        if method_path == '/':  # Путь пустой - вывод базовой информации.
            self.wfile.write('Тестовое задание для стажера на позицию «Программист на языке Python» <br><br>'.encode('utf-8'))
            self.wfile.write('Описания методов можно найти в файле readme.md <br><br>'.encode('utf-8'))
            self.wfile.write('Номер заявки: СТ-ТОМ-17838 <br>ФИО: Золотарев Максим Васильевич<br><br>'.encode('utf-8'))

        elif method_path == '/method1':  # Первый метод.
            geonameid = components.get('geonameid')
            try:
                found_city = method1(geonameid)
                self.output_city(geonameid[0], found_city)

            except TypeError:
                self.wfile.write('Введен неправильный ключ параметра.'.encode('utf-8'))

        elif method_path == '/method2':  # Второй метод.
            page = components.get('page')
            amount = components.get('amount')

            try:
                results = method2(int(page[0]), int(amount[0]))

                if results:
                    for count, city in enumerate(results):
                        self.output_city(count+1, city)
                else:
                    self.wfile.write('Конец списка'.encode('utf-8'))  # Если список пустой - скорей всего конец "книги".

            except TypeError:
                self.wfile.write('Введен неправильный ключ параметра.'.encode('utf-8'))

            except ValueError:
                self.wfile.write('Введено неправильное значение параметра.'.encode('utf-8'))

        elif method_path == '/method3':  # Третий метод.
            city1 = components.get('city1')
            city2 = components.get('city2')

            try:
                results = method3(city1, city2)

                if results:
                    self.output_city(city1[0], results[0])
                    self.output_city(city2[0], results[1])
                    self.wfile.write((results[2] + '<br><br>').encode('utf-8'))
                    self.wfile.write((results[3] + '<br><br>').encode('utf-8'))
                else:
                    self.wfile.write('Сравнение не было выполнено. Возможно, один из указанных городов не существует, '
                                     'либо была допущена ошибка в написании.'.encode('utf-8'))

            except TypeError:
                self.wfile.write('Введен неправильный ключ параметра.'.encode('utf-8'))

        elif method_path == '/method4':  # Четвертый метод
            get_name = components.get('name')

            try:
                adjusted_names = method4(get_name[0])

                if adjusted_names:
                    self.wfile.write('Возможно, вы имели ввиду: <br>'.encode('utf-8'))
                    for name in adjusted_names:
                        self.wfile.write(f'{name} <br>'.encode('utf-8'))
                else:
                    self.wfile.write('Ничего не найдено.'.encode('utf-8'))

            except TypeError:
                self.wfile.write('Введен неправильный ключ параметра.'.encode('utf-8'))

            except ValueError:
                self.wfile.write('Введено неправильное значение параметра.'.encode('utf-8'))

        else:  # Иной метод.
            self.wfile.write('Заданной функции не существует.'.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=HttpGetHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)

    with open("RU.txt", encoding='utf-8') as file:  # Чтение БД и сохранение в память.
        for lines in file:
            line = lines.split('\t')
            DB_RU.append(line)

        for city in DB_RU:
            city[3] = city[3].split(',')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


DB_RU = []
run()
