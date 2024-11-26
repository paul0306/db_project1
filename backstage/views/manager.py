from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():

    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
    
    if 'delete' in request.values:
        rname_dname = request.values.get('delete')
        rname, dname = rname_dname.split(',')
        # data = Dish.get_specific_dish(rname, dname)
        
        # if(data != None):
        #     flash('failed')
        # else:
        Dish.delete_dish(rname, dname)
    
    elif 'edit' in request.values:
        rname_dname = request.values.get('edit')
        rname, dname = rname_dname.split(',')
        return redirect(url_for('manager.dishedit', rname=rname, dname=dname))

    # dish_info = dishinfo()


    selected_branch = request.form.get('branch_select', '中山店')  # 預設為 '中山店'
    branch_data = branch()
    dish_data = dish(selected_branch)

    
    return render_template('productManager.html', dish_data = dish_data, branch_data=branch_data,
                           selected_branch=selected_branch, user=current_user.name)   #  dish_info = dish_info,


def branch():
    branch_row = Restaurant.get_all_branch()
    branch_data = []
    for i in branch_row:
        branch = {'餐廳名': i[0]}
        branch_data.append(branch)
    return branch_data

def dish(rname='中山店'):
    dish_row = Dish.get_all_dish(rname)
    dish_data = []
    for i in dish_row:
        dish = {
            '餐點名稱': i[0],
            '餐點描述': i[1],
            '餐點類別': i[2],
            '餐點價格': i[3]
        }
        dish_data.append(dish)
    return dish_data

# def dishinfo():
#     dish_db = Product.get_all_product()
#     dish_item = []
#     for i in dish_db:
#         dish = {
#             '餐點名稱': i[0],
#             '餐點價格': i[1],
#             '餐點類別': i[2],
#             '餐點描述': i[3]
#         }
#         dish_item.append(dish)
    
#     return dish_item

@manager.route('/dishadd', methods=['GET', 'POST'])
def dishadd():
    if request.method == 'POST':
        # data = ""
        # while(data != None):
        #     number = str(random.randrange( 10000, 99999))
        #     en = random.choice(string.ascii_letters)
        #     pid = en + number
        #     data = Product.get_product(pid)

        rname = request.values.get('rname')
        pname = request.values.get('pname')
        price = request.values.get('price')
        category = request.values.get('category')
        pdesc = request.values.get('description')

        # 檢查是否正確獲取到所有欄位的數據
        if rname is None or pname is None or price is None or category is None or pdesc is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.productManager'))

        # 檢查欄位的長度
        if len(pname) < 1 or len(price) < 1 or len(rname) < 1:
            flash('餐廳名稱、商品名稱或價格不可為空。')
            return redirect(url_for('manager.productManager'))
        
        Dish.add_dish(
            {'rname' : rname,
             'pname' : pname,
             'price' : price,
             'category' : category,
             'pdesc':pdesc
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')




@manager.route('/dishedit', methods=['GET', 'POST'])
@login_required
def dishedit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Dish.update_dish(
            {
            'dname' : request.values.get('dname'),
            'price' : request.values.get('price'),
            'category' : request.values.get('category'), 
            'ddesc' : request.values.get('description'),
            'rname' : request.values.get('rname')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        change_product = show_dish_info()
        return render_template('productEdit.html', data=change_product)


# def show_info():
#     pid = request.args['pid']
#     data = Product.get_product(pid)
#     pname = data[1]
#     price = data[2]
#     category = data[3]
#     description = data[4]

#     product = {
#         '餐點編號': pid,
#         '餐點名稱': pname,
#         '餐點價格': price,
#         '類別': category,
#         '餐點敘述': description
#     }
#     return product

def show_dish_info():
    rname = request.args['rname']  # 餐點編號
    dname = request.args['dname']  # 餐廳編號

    if not rname or not dname:
        return {"error": "Both 'rname' and 'dname' are required"}, 400  # 錯誤提示
    
    data = Dish.get_specific_dish(rname, dname)
    
    if not data:
        return {"error": f"No product found with rname: {rname} and dname: {dname}"}, 404
    
    rname = data[0]
    dname = data[1]
    description = data[2]
    category = data[3]
    price = data[4]

    product = {
        '餐廳名稱': rname,
        '餐點名稱': dname,
        '餐點敘述': description,
        '餐點類別': category,
        '餐點價格': price,
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購日期': i[1],
                '訂單金額': i[2],
                '付款方式': i[3],
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '餐點名稱': j[1],
                '餐點價格': j[2],
                '訂購數量': j[3],
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)


@manager.route('/reservationManager', methods=['GET', 'POST'])
@login_required
def reservationManager():
    res_row = Reservation.get_all_reservation()
    res_data = []
    for i in res_row:
        res = {
            '訂位編號': i[0],
            '餐廳名稱': i[1],
            '用餐日期': i[2],
            '訂位電話': i[3],
            '訂位姓名': i[4],
            '人數': i[5],
        }
        res_data.append(res)

    return render_template('reservationManager.html', res_data=res_data)




@manager.route('/employeeManager', methods=['GET', 'POST'])
@login_required
def employeeManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        eid = request.values.get('delete')
        # data = Record.delete_check(pid)
        
        # if(data != None):
        #     flash('failed')
        # else:
            # data = Product.get_product(pid)
        Employee.delete_employee(eid)
    
    elif 'edit' in request.values:
        eid = request.values.get('edit')
        return redirect(url_for('manager.editemployee', eid=eid))
    
    employee_data = employee_info()
    return render_template('employeeManager.html', employee_data = employee_data)

def employee_info():
    employee_row = Employee.get_all_employee()
    employee_data = []
    for i in employee_row:
        employee = {
            '餐廳名稱': i[0],
            '員工編號': i[1],
            '員工電話': i[2],
            '員工姓名': i[3],
            '職位': i[4]
        }
        employee_data.append(employee)
    return employee_data


@manager.route('/employeeadd', methods=['GET', 'POST'])
def employeeadd():
    if request.method == 'POST':
        # data = ""
        # while(data != None):
        #     number = str(random.randrange( 10000, 99999))
        #     en = random.choice(string.ascii_letters)
        #     pid = en + number
        #     data = Product.get_product(pid)

        rname = request.values.get('rname')
        ephone = request.values.get('ephone')
        ename = request.values.get('ename')
        position = request.values.get('position')

        # 檢查是否正確獲取到所有欄位的數據
        if rname is None or rname is None or ephone is None or ename is None or position is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.employeeManager'))

        # 檢查欄位的長度
        if len(rname) < 1 or len(ephone) < 1 or len(ename) < 1:
            flash('餐廳名稱、員工電話或員工姓名不可為空。')
            return redirect(url_for('manager.employeeManager'))

        Employee.add_employee(
            {
             'rname' : rname,
             'ephone' : ephone,
             'ename' : ename,
             'position' : position
            }
        )

        return redirect(url_for('manager.employeeManager'))
    
    return render_template('employeeManager.html')

@manager.route('/editemployee', methods=['GET', 'POST'])
@login_required
def editemployee():
    if request.method == 'GET':
        if(current_user.role == 'user'): # Ensure appropriate access control
            flash('No permission')
            return redirect(url_for('index'))
    
    if request.method == 'POST':
        Employee.update_employee(
            {
                'rname': request.values.get('rname'),
                'ephone': request.values.get('ephone'),
                'ename': request.values.get('ename'),
                'position': request.values.get('position'),
                'eid': request.values.get('eid')
            }
        )
        return redirect(url_for('manager.employeeManager'))
    
    else:
        employee_data = show_employee_info()
        return render_template('employeeEdit.html', data = employee_data)

def show_employee_info():
    eid = request.args['eid']  # 員工編號

    if not eid :
        return {"error": "'eid' are required"}, 400  # 錯誤提示
    
    data = Employee.get_specific_employee(eid)
    
    if not data:
        return {"error": f"No product found with eid: {eid}"}, 404
    
    # Fetch restaurant names
    restaurants = Restaurant.get_all_branch()

    rname = data[0]
    eid = data[1]
    ephone = data[2]
    ename = data[3]
    position = data[4]

    employee = {
        '餐廳名稱': rname,
        '員工編號': eid,
        '員工電話': ephone,
        '員工姓名': ename,
        '職位': position,
        '所有餐廳': [r[0] for r in restaurants]
    }
    return employee