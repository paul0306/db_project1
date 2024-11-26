from typing import Optional
import psycopg2
from psycopg2 import pool


class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  # 最小和最大連線數
        user='project_18',
        password='umuu93',
        host='140.117.68.66',
        port='5432',
        dbname='project_18'
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input):
        if not isinstance(input, (tuple, list)):
            raise TypeError(f"Input should be a tuple or list, got: {type(input).__name__}")
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def execute(sql):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)


class Member:
    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, mid, identity, name FROM member WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM member"
        return DB.fetchall(sql)
    
    @staticmethod
    def get_all_name():
        sql = "SELECT name FROM member"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO member (name, account, password, identity) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['password'], input_data['identity']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_role(userid):
        sql = 'SELECT identity, name FROM member WHERE mid = %s'
        return DB.fetchone(sql, (userid,))


#####################################################

class Dish():
    # 列出該家分店所有餐點
    @staticmethod
    def get_all_dish(rname):
        sql = 'SELECT dname, description, type, price FROM dish WHERE rname = %s'
        return DB.fetchall(sql, (rname,))
    
    @staticmethod
    def get_specific_dish(rname, dname):
        sql = 'SELECT * FROM dish WHERE rname = %s AND dname = %s'
        return DB.fetchone(sql, (rname, dname))
    
    # 修改餐點
    @staticmethod
    def update_dish(input_data):
        sql = 'UPDATE dish SET price=%s, type=%s, description=%s WHERE rname=%s AND dname=%s'
        DB.execute_input(sql, (input_data['price'], input_data['category'], input_data['ddesc'], input_data['rname'], input_data['dname']))

    # 新增餐點
    @staticmethod
    def add_dish(input_data):
        sql = 'INSERT INTO dish (rname, dname, price, type, description) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['rname'], input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc']))

    # 刪除餐點
    @staticmethod
    def delete_dish(rname, dname):
        sql = 'DELETE FROM dish WHERE rname = %s AND dname = %s'
        DB.execute_input(sql, (rname, dname))

    def count():
        sql = 'SELECT COUNT(*) FROM dish'
        return  DB.fetchone(sql)

class Restaurant():
    # 列出所有分店
    @staticmethod
    def get_all_branch():
        sql = 'SELECT rname FROM restaurant'
        return DB.fetchall(sql)

class Reservation():
    @staticmethod
    def get_all_reservation():
        sql = 'SELECT * FROM reservation'
        return DB.fetchall(sql)
    
    @staticmethod
    def add_reservation(input_data):
        sql = 'INSERT INTO reservation (rsname, rname, rsdate, rsphone, rsamount) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['rsname'], input_data['rname'], input_data['rsdate'], input_data['rsphone'], input_data['rsamount']))

class Employee():
    @staticmethod
    def get_all_employee():
        sql = 'SELECT * FROM employee'
        return DB.fetchall(sql)
    
    @staticmethod
    def get_specific_employee(eid):
        sql = 'SELECT * FROM employee WHERE eid = %s'
        return DB.fetchone(sql, (eid,))
    
    @staticmethod
    def add_employee(input_data):
        sql = 'INSERT INTO employee (rname, ephone, ename, position) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['rname'], input_data['ephone'], input_data['ename'], input_data['position']))
    
    @staticmethod
    def delete_employee(eid):
        sql = 'DELETE FROM employee WHERE eid = %s'
        DB.execute_input(sql, (eid,))
    
    @staticmethod
    def update_employee(input_data):
        sql = 'UPDATE employee SET rname = %s, ephone = %s, ename = %s, position = %s WHERE eid = %s'
        DB.execute_input(sql, (input_data['rname'], input_data['ephone'], input_data['ename'], input_data['position'],input_data['eid']))
###################################################

class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM cart, record 
                 WHERE cart.mid = %s::bigint 
                 AND cart.tno = record.tno::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))


class Product:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM product'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(pid):
        sql = 'SELECT * FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))
    

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM product'
        return DB.fetchall(sql)

    @staticmethod
    def get_name(pid):
        sql = 'SELECT pname FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO product (pid, pname, price, category, pdesc) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc']))

    @staticmethod
    def delete_product(pid):
        sql = 'DELETE FROM product WHERE pid = %s'
        DB.execute_input(sql, (pid,))

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE product SET pname = %s, price = %s, category = %s, pdesc = %s WHERE pid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc'], input_data['pid']))


class Record:
    @staticmethod
    def get_total_money(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]

    @staticmethod
    def check_product(pid, tno):
        sql = 'SELECT * FROM record WHERE pid = %s and tno = %s'
        return DB.fetchone(sql, (pid, tno))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO record (pid, tno, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['tno'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(tno):
        sql = 'SELECT * FROM record WHERE tno = %s'
        return DB.fetchall(sql, (tno,))

    @staticmethod
    def get_amount(tno, pid):
        sql = 'SELECT amount FROM record WHERE tno = %s and pid = %s'
        return DB.fetchone(sql, (tno, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE record SET amount = %s, total = %s WHERE pid = %s and tno = %s'
        DB.execute_input(sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['tno']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]


class Order_List:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO order_list (oid, mid, ordertime, price, tno) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'], input_data['format'], input_data['total'], input_data['tno']))

    @staticmethod
    def get_order():
        sql = 'SELECT * FROM "order"'
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT o.oid, p.pname, r.saleprice, r.amount
        FROM order_list o
        JOIN record r ON o.tno = r.tno -- 確保兩者都是 bigint 類型
        JOIN product p ON r.pid = p.pid
        '''
        return DB.fetchall(sql)


class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(total), category FROM product, record WHERE product.pid = record.pid GROUP BY category'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
