#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal
from collections import defaultdict
import sys
sys.stdin = open('input.txt')


def input_data():
    """Получаем данные от пользователя"""
    # Общая ёмкость всего рюкзака
    capacity = Decimal(input())

    # Таблица с инфомацией о предметах
    info_table = dict()

    # Обходим все предметы, что есть
    for line in sys.stdin:
        # Собираем параметры для каждого предмета
        name, *numbers = line.split()
        # Числовые парметры (размер и цена) приводим к типу Decimal
        size, price = map(Decimal, numbers)
        # Добавляем строку c информацией о предмете к таблице
        info_table[name] = [size, price]

    # результат обработки данных от пользователя - это
    # возможная вмещаемость рюкзака и таблица с информацией
    return capacity, info_table


def get_step_capacity(info_table):
    """
    Получить шаг емкости подрюкзаков
    info_table - таблица с информацией обо всех предметах
    """
    # По сути это задача нахождения Наибольшего Общего Делителя (НОД)
    # для всех размеров предметов

    # Множество размеров всех предметов
    # У нескольких предметов может быть один и тот же размер
    # Чтобы ускорить вычисления испольуем множество, а не список
    sizes = set()
    # проходим все предметы и заполняем множество
    for bp_item, [size, price] in info_table.items():
        sizes.add(size)

    # Размер минимального предмета в рюкзаке - это первоначальное приближение
    # значения шага подрюкзаков
    step = min(sizes)

    # Пока не найдём нужный оптимальный шаг
    while True:
        # Обходим размеры всех предметов в наборе
        for size in sizes:
            # Находим значение остатка от деления размера предмета на шаг
            remainder = size % step
            # если остаток от деления НЕ нулевой
            if remainder != Decimal('0'):
                # Назначаем новый шаг
                step = remainder
                # И выходим из внутреннего цикла for
                # Возвращаемся к while
                break
        else:
            # Если цикл for отработал без обрывания break
            # Значит мы нашли нужный шаг
            return step


def find_optimal_set(capacity, info_table):
    """Найти оптимальный набор предметов"""
    # Заготовка для таблицы с вычислениями
    calc_table = defaultdict(lambda: defaultdict(dict))
    # Шаг размеров подрюкзаков
    step = get_step_capacity(info_table)
    # Размеры подрюкзаков - массив чисел Decimal
    cols = [step*i for i in range(1, int(capacity / step)+1)]

    # Сначала заполним таблицу нулями - оценка текущей стоимости
    # Также в каждой ячейки зададим пустой набор элементов
    # Обходим все предметы из данных пользователя
    for bp_item in info_table:
        # Для данного предмета - строки
        # создаём int(capacity / step) столбцов - размеры подрюкзаков
        for size in cols:
            # Даём ячейкам таблицы первоначальные значения
            calc_table[bp_item][size] = {'score': 0, 'items': set()}

    # Заполняем построчно таблицу для расчётов
    # Нам понадобится переменная, запоминимающая название предыдущего предмета
    before_item = None
    # Обходим все строки таблицы
    for bp_item, [cur_size, cur_price] in info_table.items():
        # Обходим столбцы текущей строки
        for size in cols:
            # Сначала находим предыдущую строку
            before_row = calc_table[before_item]
            # Если она существует
            if before_row:
                # Находим предыдущий максимум
                before_max = before_row[size]['score']
                # Предыдущий набор элементов
                before_set = before_row[size]['items']

                # Если размер предмета равен размеру подрюкзака
                if cur_size == size:
                    # Новый максимум - цена текущего предмета
                    new_max = cur_price
                    # Новый набор состоит только из самого предмета
                    new_set = {bp_item}
                elif cur_size > size:
                    # Если объём текущего элемента больше размера подрюкзака
                    # То этот предмет еще нельзя положить в рюкзак
                    # Значит значение текущего максимума = 0
                    new_max = 0
                    # Новый набор элементов тоже будет пустым,
                    # так как их нет в этом случае
                    new_set = set()
                else:
                    # Иначе вычисляем значение текущего максимума, состояшего из
                    # цены текушего элемента + ценность оставшегося пространства
                    new_max = cur_price + before_row[size-cur_size]['score']
                    # Новый набор элементов - текущий с предыдущими
                    new_set = {bp_item, *before_row[size-cur_size]['items']}

                # Теперь находим максимальную цену для текущего подрюкзака
                # И заполняем ячейку таблицы
                if new_max > before_max:
                    calc_table[bp_item][size]['score'] = new_max
                    calc_table[bp_item][size]['items'] = new_set
                else:
                    calc_table[bp_item][size]['score'] = before_max
                    calc_table[bp_item][size]['items'] = before_set
            else:
                # Если предыдущей подстроки не существует
                # То сначала проверяем можно ли запихнуть текущий предмет
                # в имеющийся объём, если нельзя
                if cur_size > size:
                    # Значит значение текущего максимума = 0
                    calc_table[bp_item][size]['score'] = 0
                    # Новый набор элементов тоже будет пустым,
                    # так как их нет в этом случае
                    calc_table[bp_item][size]['items'] = set()
                else:
                    # Можно, то сразу заполняем значения для ячейки
                    calc_table[bp_item][size]['score'] = cur_price
                    calc_table[bp_item][size]['items'] = {bp_item}

        # Прошли всю строку
        # Задаём значение предыдущего предмета - текущий
        before_item = bp_item

    # Получаем набор элементов в рюкзаке
    bp_set = calc_table[bp_item][cols[-1]]['items']

    # Возвращаем их
    return bp_set


def main():
    """Основная программа"""
    # Получаем данные от пользователя
    capacity, info_table = input_data()
    # Решаем задачу, получая набор предметов
    bp_set = find_optimal_set(capacity, info_table)
    # Выводим результаты
    # Итоговая ценность
    score = 0
    # Итоговый суммарный объём
    volume = 0
    print(f'Набор предметов в рюкзаке емкостью "{capacity}":')
    # Заголовок таблицы
    print(f'\t{"Предмет":^10}| размер | ценность |')
    print('-'*40)
    # Строки с предметами
    for bp_item in sorted(bp_set):
        size, price = info_table[bp_item]
        print(f'\t{bp_item:<10}|{size:>8}|{price:>10}|')
        volume += size
        score += price
    # Итоговая самая нижняя строка
    print('-'*40)
    print(f'\t{"СУММА":<10}|{volume:>8}|{score:>10}|')


# Стартовая точка запуска программы
if __name__ == "__main__":
    main()
