import pymysql
import datetime


class Dbbot:
    # def __init__(self, db_file_name):
    #     """создание или подключение к бд"""
    #
    #     self.connect = sqlite3.connect(f'{db_file_name}.db')
    #     self.cursor = self.connect.cursor()

    def __init__(self, db_file_name):
        try:
            self.connect = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='1234',
            database = 'hui'
)
            print("successfully connected...")
            print("#" * 20)

            self.cursor = self.connect.cursor()



        except Exception as ex:
            print("Connection refused...")
            print(ex)

    def check_or_get(self, obj, where, znach):
        self.cursor.execute(
            f"select {obj} from users where {where} = {znach};"
        )

        return self.cursor.fetchall()




    def table_creater(self, table_name, sql_comand):
        """создать таблицу"""
        a = f"CREATE TABLE IF NOT EXISTS `{table_name}`(id int AUTO_INCREMENT," \
            f" {sql_comand}," \
            "PRIMARY KEY (id))"
        self.cursor.execute(a)

    def cols_list(self, table_name):
        list_of_col = self.cursor.execute(f'select * from {table_name}')
        names = [description[0] for description in self.cursor.description]

        return names

    def add_to_table(self, table_name, args):
        """добавление данных в таблицу"""

        names = self.cols_list(table_name)
        data = list(args)
        for i in range(len(names)-len(args)):
            data.append(0)

        insert_query = f"insert into {table_name}({','.join(names)}) values{tuple(data)};"
        self.cursor.execute(insert_query)

        return self.connect.commit()

    def update_data_in_table(self, table_name, id, param='id' , arg=list()):
        table_c = self.cols_list(table_name)
        for i in range(1, len(table_c)):
            if arg[i] != '-':
                self.cursor.execute(f"UPDATE {table_name} SET {table_c[i]} = {arg[i]} WHERE {param}={id};")
        return self.connect.commit()

    def reader(self, table_name):
        """чтение таблицы"""
        select_all_rows = f"SELECT * FROM `{table_name}`"
        self.cursor.execute(select_all_rows)

        rows = self.cursor.fetchall()
        return rows



    def list_of_tables(self):
        """Вывод всех таблиц"""
        self.cursor.execute("show tables;")
        return self.cursor.fetchall()

    def deleter(self, type_of_del_item, table_name, id=0):
        """удаление таблицы или записи в таблице"""
        if type_of_del_item == "table":
            self.cursor.execute(f"drop table {table_name};")

        elif type_of_del_item == "string":
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id={id};")
            return self.connect.commit()

    def cons_cols(self, a):
        self.cursor.execute(f"alter table users add {a} bool default 0")

    def del_cols(self, a):
        self.cursor.execute(f"alter table users DROP COLUMN {a};")

    def clean_sql_command(self, sqlcommand):
        self.cursor.execute(f"{sqlcommand}")
        return self.connect.commit()

    def close_connection(self):
        self.connect.close()
        self.cursor.close()

# Database = Dbbot('bd')
# print(a.check_or_get('username', 'role1', 1))
# a.table_creater('roles','Спонсор bool, Передержка bool')
# a.table_creater('users','join_date datetime, user_id bigint , username varchar(50), name varchar(50)') #ok
# print(list(set(Database.check_or_get("username", f"{tag}", 1) for tag in ['role1', 'role2']))[0])
# a.cons_cols("role3")

# Dbbott.update_data_in_table('users', 14, "id",["-","-","@DOICHLANDP","-"])
# print(Database.list_of_tables())
# print(Dbbott.cols_list('users')[5:])
# print(table_former(a.reader('jopa'), a.cols_list("jopa"))) #ok


# print(Database.add_to_table('users', [0, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1033354958, "@Gomos1nist", "Gdwada"]))
# a.deleter('string', 'jopa', 1) ok
# a.update_data_in_table('jopa', 1, 1432)

