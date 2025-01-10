import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox as mb
from typing import Optional
from functools import partial
import models
import serializers
import enum
import search
from playhouse.shortcuts import model_to_dict
import json
import openpyxl
import time
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

def on_drive(file_name):
    drive = GoogleDrive(gauth)
    my_file = drive.CreateFile({'title':f'{file_name}'})
    my_file.SetContentFile(file_name)
    my_file.Upload()

class Table_name (enum.Enum):
    NOTHING = 0
    OBJECTS = 1
    RIGHTS = 2
    CARS = 3
    DRIVERS = 4
    CARGO = 5
    ORGANIZATIONS = 6
    CUSTOMERS = 7
    ORDERS = 8
    OPERATIONS = 9

class Types_user (enum.Enum):
    NOTHING = -1
    NOT_REGISTTERED = 0
    REGISTTERED = 1

type_user = Types_user.NOTHING

class Table():
    def __init__(self, model, serializer, columns_name):
        self.model = model
        self.serializer = serializer
        self.columns_name = columns_name

class Registration_window(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        name_space = tk.Frame()
        self.entrys = list()
        label = tk.Label(name_space, text='Имя', bg='#d7d8e0')
        label.pack(side=tk.LEFT)

        entry = tk.Entry(name_space, width=30)
        entry.pack(side=tk.LEFT)
        self.entrys.append(entry)
        name_space.pack(side=tk.TOP)

        password_space = tk.Frame()
        label = tk.Label(password_space, text='Пароль', bg='#d7d8e0')
        label.pack(side=tk.LEFT)

        entry = tk.Entry(password_space, width=30)
        entry.pack(side=tk.LEFT)
        self.entrys.append(entry)
        password_space.pack(side=tk.TOP)

        buttons_space = tk.Frame()
        tk.Button(
            buttons_space,
            text='Авторизироваться',
            command=partial(self.__authorization),
            width=30,
            bd=2,
            compound=tk.TOP,
        ).pack(side=tk.BOTTOM)

        tk.Button(
            buttons_space,
            text='Войти без авторизации',
            command=partial(self.__not_authorization),
            width=20,
            bd=2,
            compound=tk.TOP,
        ).pack(side=tk.BOTTOM)

        buttons_space.pack(side=tk.BOTTOM)

    def __authorization(self):
        data = list()
        for entry in self.entrys:
            data.append(entry.get())

        query = models.Account.select().where(models.Account.name == data[0]).where(models.Account.password == data[1])
        if query.exists():
            global type_user
            type_user = Types_user.REGISTTERED
            self.root.destroy()
        else:
            mb.showerror(title="Ошибка", message="Не удалось авторизоваться")

    def __not_authorization(self):
        global type_user
        type_user = Types_user.NOT_REGISTTERED
        self.root.destroy()
        
class Main(tk.Frame):
    """Главный экран графического приложения"""
    def __init__(self, root):
        super().__init__(root)
        self.__current_table = Table_name.NOTHING
        style = ttk.Style()
        style.configure("Treeview.Heading", font="helvetica 10")
        style.configure("Treeview", font="helvetica 10")
        # Табличное представление
        self.tree: Optional[ttk.Treeview] = None  
        self.search_entrys = list()
        self.__current_page = list()
        # Пункты меню и функции получения данных идентичны примеру из лабораторной работы №5
        self.__entities = {
            Table_name.OBJECTS: 'Объекты',
            Table_name.RIGHTS: 'Права',
            Table_name.CARS: 'Машины',
            Table_name.DRIVERS: 'Водители',
            Table_name.CARGO: 'Грузы',
            Table_name.ORGANIZATIONS: 'Организации',
            Table_name.CUSTOMERS: 'Заказчик',
            Table_name.ORDERS: 'Заказ',
            Table_name.OPERATIONS: 'Операции'
        }

        self.__tables = {
            Table_name.OBJECTS: Table(models.Objects, serializers.serialize_objects, ['ID', 'Тип', 'Адрес']),
            Table_name.RIGHTS: Table(models.Rights, serializers.serialize_rights, ['ID', 'Название']),
            Table_name.CARS: Table(models.Cars, serializers.serialize_cars, ['ID', 'Модель', 'Номер', 'Статус', 'ID объекта', 'Права']),
            Table_name.DRIVERS: Table(models.Drivers, serializers.serialize_drivers, ['ID', 'ФИО', 'Права', 'ID машины']),
            Table_name.CARGO: Table(models.Cargo, serializers.serialize_cargo, ['ID', 'Описание']),
            Table_name.ORGANIZATIONS: Table(models.Organizations, serializers.serialize_organizations, ['ID', 'Название']),
            Table_name.CUSTOMERS: Table(models.Customers, serializers.serialize_customers, ['ID', 'ФИО', 'Телефон', 'ID организации']),
            Table_name.ORDERS: Table(models.Orders, serializers.serialize_orders, ['ID', 'Описание', 'Начальная дата', 'Конечная дата', 'Статус', 'Цена', 'ID заказчика']),
            Table_name.OPERATIONS: Table(models.Operations, serializers.serialize_operations, ['ID', 'Дата операции', 'Начальный адрес', 'Конечный адрес', 'ID машины', 'ID груза', 'ID водителя', 'ID заказа'])
        }

        self.__search_func = {
            Table_name.OBJECTS: search.search_objects_by_pattern,
            Table_name.RIGHTS: search.search_rights_by_pattern,
            Table_name.CARS: search.search_cars_by_pattern,
            Table_name.DRIVERS: search.search_drivers_by_pattern,
            Table_name.CARGO: search.search_cargo_by_pattern,
            Table_name.ORGANIZATIONS: search.search_organizations_by_pattern,
            Table_name.CUSTOMERS: search.search_customers_by_pattern,
            Table_name.ORDERS: search.search_orders_by_pattern,
            Table_name.OPERATIONS: search.search_operations_by_pattern
        }

        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        tk.Button(
            toolbar,
            text='Меню',
            command=partial(self.__create_menu),
            bd=2,
            compound=tk.TOP,
            padx=10
        ).pack(side=tk.LEFT)
        for option, name in self.__entities.items():
            # Создаём каждый объект и упаковываем их на toolbar
            tk.Button(
                toolbar,
                text=name,
                # Функция, которая выполняется при нажатии на кнопку.
                # Это функция вывода таблицы, и кортеж из функции получения данных и имён столбцов таблицы
                command=partial(self.__table_result, option),
                bd=2,
                compound=tk.TOP,
                padx=10
            ).pack(side=tk.LEFT)

        toolbar.pack(side=tk.TOP)

        self.__create_menu()

    def __create_menu(self):
        self.__destroy_curret_page()
        menu_space = tk.Frame(bd=2)
        tk.Button(
            menu_space,
            text='Создать резервную копию',
            command=partial(self.__create_backup),
            bd=2,
            compound=tk.TOP,
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            menu_space,
            text='Экспортировать данные',
            command=partial(self.__export_data),
            bd=2,
            compound=tk.TOP,
        ).pack(side=tk.LEFT, padx=20)

        menu_space.pack(anchor=tk.CENTER, expand=True)
        self.__current_page.append(menu_space)

    def __create_backup(self):
        name = 'backup' + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(time.time())) + '.xlsx'
        wb = openpyxl.Workbook()
        for key in self.__tables:
            columns_name = self.__tables[key].columns_name
            models = self.__tables[key].model
            serializer = self.__tables[key].serializer
            ws = wb.active
            ws.append(columns_name)
            for model in models:
                dict = serializer(model)
                data = list()
                for d in dict:
                    data.append(d)
                ws.append(data)

        wb.save(name)
        on_drive(name)


    def __export_data(self):
        frame = tk.Toplevel()
        frame.title('Экспорт данных')
        frame.geometry("300x200")

        table_space = tk.Frame(frame)
        label = tk.Label(table_space, text='Выберите таблицу', bg='#d7d8e0')
        label.pack(side=tk.LEFT)

        tables = {'Объекты': Table_name.OBJECTS,
            'Права': Table_name.RIGHTS,
            'Машины': Table_name.CARS,
            'Водители': Table_name.DRIVERS,
            'Грузы': Table_name.CARGO,
            'Организации': Table_name.ORGANIZATIONS,
            'Заказчики': Table_name.CUSTOMERS,
            'Заказы': Table_name.ORDERS,
            'Операции': Table_name.OPERATIONS
            }

        keys = list()
        for key in tables.keys():
            keys.append(key)

        combobox_table = ttk.Combobox(table_space, values=keys)
        combobox_table.pack(side=tk.LEFT)
        table_space.pack(side=tk.TOP)

        type_space = tk.Frame(frame)
        label = tk.Label(type_space, text='Выберите формат', bg='#d7d8e0')
        label.pack(side=tk.LEFT)

        types = ('json', 'xlsx')
        combobox_type = ttk.Combobox(type_space, values=types)
        combobox_type.pack(side=tk.LEFT)
        type_space.pack(side=tk.TOP)
        
#self.__tables[tables[combobox_table.get()]]
        def __export(self, combobox_table, combobox_type, frame):
            models = self.__tables[tables[combobox_table.get()]].model
            columns_name = self.__tables[tables[combobox_table.get()]].columns_name
            serializer = self.__tables[tables[combobox_table.get()]].serializer
            name = models._meta.table_name + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(time.time()))
            type = combobox_type.get()

            if type == 'json':
                with open('C:/Users/User/Downloads/' + name + '.json', 'w') as f:
                    for model in models:
                        json.dump(model_to_dict(model), f)

                    f.close()

                frame.destroy()
            if type == 'xlsx':
                wb = openpyxl.Workbook()

                ws = wb.active
                ws.append(columns_name)
                for model in models:
                    dict = serializer(model)
                    data = list()
                    for d in dict:
                        data.append(d)
                    ws.append(data)

                wb.save('C:/Users/User/Downloads/' + name + '.xlsx')

                frame.destroy()

        tk.Button(
            frame,
            text='Экспортировать данные',
            command=partial(__export, self, combobox_table, combobox_type, frame),
            bd=2,
            compound=tk.TOP,
        ).pack(side=tk.BOTTOM)


    def __insert(self):
        if self.__current_table == Table_name.NOTHING:
            mb.showerror(title="Ошибка", message="Не выбрана таблица")
            return
        
        frame = tk.Toplevel()
        frame.title('Добавить')
        frame.geometry("500x500")
        frame.columns = self.__tables[self.__current_table].columns_name

        frame.entrys = list()
        frame.protocol("WM_DELETE_WINDOW", lambda: self.__dismiss(frame))

        for i in range(0, len(frame.columns)):
            label = tk.Label(frame, text=frame.columns[i])
            label.pack(anchor=tk.NW)

            entry = tk.Entry(frame)
            entry.pack(anchor=tk.NE, fill=tk.X)
            frame.entrys.append(entry)

        tk.Button(
            frame,
            text="Добавить",
            command=partial(self.__button_insert, frame),
            bg='#d7d8e0',
            bd=0,
            compound=tk.BOTTOM,
            padx=10
        ).pack(side=tk.BOTTOM)
        
        frame.grab_set()

    def __button_insert(self, frame):
        data = dict()
        column_names = [field.name for field in self.__tables[self.__current_table].model._meta.sorted_fields]
        for i in range(0, len(column_names)):
            if frame.entrys[i].get() == 'None':
                 data.update({column_names[i]: None})
            else:
                data.update({column_names[i]: frame.entrys[i].get()})
        
        self.__tables[self.__current_table].model.create(**data)

        self.__table_result(self.__current_table)
        self.__dismiss(frame)

    def __change(self):
        if self.__current_table == Table_name.NOTHING:
            mb.showerror(title="Ошибка", message="Не выбрана таблица")
            return

        if self.__current_table == '6' or self.__current_table == '8':
            mb.showerror(title="Ошибка", message="Таблица не может быть изменена")
            return

        selected_item = self.tree.selection()
        if len(selected_item) == 0:
            mb.showerror(title="Ошибка", message="Не выбрана строка")
            return

        frame = tk.Toplevel()
        frame.title('Изменить')
        frame.geometry("500x500")
        frame.columns = self.__tables[self.__current_table].columns_name

        frame.entrys = list()
        frame.protocol("WM_DELETE_WINDOW", lambda: self.__dismiss(frame))

        next_field = 0
        if (self.__current_table == '5'):
            for i in range(0, 2):
                label = tk.Label(frame, text=frame.columns[i])
                label.pack(anchor=tk.NW)

                entry = tk.Entry(frame)
                entry.pack(anchor=tk.NE, fill=tk.X)
                entry.insert(0, self.tree.item(selected_item)['values'][i])
                entry.config(state='readonly')
                frame.entrys.append(entry)

            next_field = 2
        else:
            label = tk.Label(frame, text=frame.columns[0])
            label.pack(anchor=tk.NW)

            entry = tk.Entry(frame)
            entry.pack(anchor=tk.NE, fill=tk.X)
            entry.insert(0, self.tree.item(selected_item)['values'][0])
            entry.config(state='readonly')
            frame.entrys.append(entry)

            next_field = 1

        for i in range(next_field, len(frame.columns)):
            label = tk.Label(frame, text=frame.columns[i])
            label.pack(anchor=tk.NW)

            entry = tk.Entry(frame)
            entry.pack(anchor=tk.NE, fill=tk.X)
            entry.insert(0, self.tree.item(selected_item)['values'][i])
            frame.entrys.append(entry)

        tk.Button(
            frame,
            text="Изменить",
            command=partial(self.__button_change, frame),
            bg='#d7d8e0',
            bd=0,
            compound=tk.BOTTOM,
            padx=10
        ).pack(side=tk.BOTTOM)
        
        frame.grab_set()

    def __button_change(self, frame):
        data = dict()
        column_names = [field.name for field in self.__tables[self.__current_table].model._meta.sorted_fields]
        for i in range(0, len(column_names)):
            if frame.entrys[i].get() == 'None':
                 data.update({column_names[i]: None})
            else:
                data.update({column_names[i]: frame.entrys[i].get()})
        
        self.__tables[self.__current_table].model.update(data).where(self.__tables[self.__current_table].model.id == data['id']).execute()

        self.__table_result(self.__current_table)
        self.__dismiss(frame)

    def __delete(self):
        if self.__current_table == Table_name.NOTHING:
            mb.showerror(title="Ошибка", message="Не выбрана таблица")
            return

        selected_item = self.tree.selection()
        if len(selected_item) == 0:
            mb.showerror(title="Ошибка", message="Не выбрана строка")
            return
        
        self.__tables[self.__current_table].model.delete().where(self.__tables[self.__current_table].model.id == self.tree.item(selected_item)['values'][0]).execute()

        self.__table_result(self.__current_table)

    def __find(self):
        data = list()
        for i in range(0, len(self.search_entrys)):
            data.append(self.search_entrys[i].get())

        query = self.__search_func[self.__current_table](self.__tables[self.__current_table].model, data)
        self.table_space.destroy()

        self.table_space = tk.Frame(self.__main_workplace, bg='#d7d8e0', bd=2)  
        self.__show_result(query, self.__tables[self.__current_table].serializer, self.__tables[self.__current_table].columns_name)
        self.table_space.pack(side=tk.BOTTOM)
        self.__current_page.append(self.table_space)

    def __dismiss(self, window):
        window.grab_release() 
        window.destroy()

    def __destroy_curret_page(self):
        for object in self.__current_page:
            object.destroy()

    def __create_search_entrys(self, columns_name):
        self.search_entrys.clear()
        search_space = tk.Frame(self.__main_workplace)
        label = tk.Label(search_space, text=columns_name[0], bg='#d7d8e0')
        label.pack(side=tk.LEFT)

        entry = tk.Entry(search_space, width=8)
        entry.pack(side=tk.LEFT)
        self.search_entrys.append(entry)

        for i in range(1, len(columns_name)):
            label = tk.Label(search_space, text=columns_name[i], bg='#d7d8e0')
            label.pack(side=tk.LEFT)

            entry = tk.Entry(search_space, width=15)
            entry.pack(side=tk.LEFT)
            self.search_entrys.append(entry)

        tk.Button(
            search_space,
            text="Найти",
            command=partial(self.__find),
            bd=2,
            compound=tk.TOP,
            padx=10
        ).pack(side=tk.LEFT)

        search_space.pack(side=tk.TOP)

        self.__current_page.append(search_space)

    def __create__table_buttons(self):
        table_buttons_space = tk.Frame(self.__main_workplace, bg='#d7d8e0', bd=2)
        tk.Button(
            table_buttons_space,
            text="Добавить",
            command=partial(self.__insert),
            bd=2,
            compound=tk.TOP,
            padx=10
        ).pack(side=tk.LEFT)

        tk.Button(
            table_buttons_space,
            text="Изменить",
            command=partial(self.__change),
            bd=2,
            compound=tk.TOP,
            padx=10
        ).pack(side=tk.LEFT)

        tk.Button(
            table_buttons_space,
            text="Удалить",
            command=partial(self.__delete),
            bd=2,
            compound=tk.TOP,
            padx=10
        ).pack(side=tk.LEFT)

        table_buttons_space.pack(side=tk.BOTTOM)
        self.__current_page.append(table_buttons_space)


    def __table_result(self, table):
        self.__destroy_curret_page()
        self.__main_workplace = tk.Frame()
        self.table_space = tk.Frame(self.__main_workplace, bg='#d7d8e0', bd=2) 
        if(type_user == Types_user.REGISTTERED):
            self.__create__table_buttons()
        self.__create_search_entrys(self.__tables[table].columns_name) 
        self.__show_result(self.__tables[table].model.select(), self.__tables[table].serializer, self.__tables[table].columns_name)
        self.table_space.pack(side=tk.BOTTOM)
        self.__current_page.append(self.table_space)
        self.__set_curret_table(table)
        self.__main_workplace.pack(side=tk.TOP)
        self.__current_page.append(self.__main_workplace,)

    def __set_curret_table(self, table):
        self.__current_table = table

    def __show_result(self, query, serializer, columns_name): 
        # Создаём новую таблицу
        self.tree = ttk.Treeview(self.table_space, columns=columns_name, height=len(query), show='headings')

        columns = [serializer(model) for model in query]
        size_columns = list(len(column) for column in columns_name)
        for row in columns:
            val = list(row.values())
            for i in range (0, len(val)):
                size_columns[i] = max(size_columns[i], len(str(val[i])))
        
        def __sort(col, reverse):
            # получаем все значения столбцов в виде отдельного списка
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
            # сортируем список
            l.sort(reverse=reverse)
            # переупорядочиваем значения в отсортированном порядке
            for index,  (_, k) in enumerate(l):
                self.tree.move(k, "", index)
            # в следующий раз выполняем сортировку в обратном порядке
            self.tree.heading(col, command=lambda: __sort(col, not reverse))

        scrollbar_y = ttk.Scrollbar(self.table_space, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(self.table_space, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Заполняем каждый столбец именами столбцов
        for i in range(0, len(columns_name)):
            self.tree.column(columns_name[i], width=size_columns[i] * 10, minwidth=size_columns[i] * 10, anchor=tk.CENTER)
            self.tree.heading(columns_name[i], text=columns_name[i], command=partial (__sort, i, False))
        self.tree.pack(side=tk.LEFT)

        # Заполняем таблицу данными
        for row in columns:
            self.tree.insert('', 'end', values=list(row.values()))
        __sort(0, False)

if __name__ == '__main__':
    root_registration = tk.Tk()
    root_registration.title("Авторизация")
    root_registration.geometry("600x350")
    app_registration = Registration_window(root_registration)
    app_registration.pack()
    root_registration.mainloop()

    if(type_user != Types_user.NOTHING):
        root = tk.Tk()
        root.title("Курсовая работа")
        root.geometry("1400x600")
        app = Main(root)
        app.pack()
        root.mainloop()