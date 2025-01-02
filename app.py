from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
from werkzeug.utils import secure_filename
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from interactive import (
    select_fields, 
    get_field_selectors, 
    format_field_value, 
    display_results,
    handle_error
)

app = Flask(__name__)
CORS(app)

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB限制

# 创建上传文件夹
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 配置静态文件路径
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 获取所有货物
@app.route('/api/goods', methods=['GET'])
def get_goods():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('SELECT * FROM goods')
    goods = [{'id': row[0], 'name': row[1], 'category': row[2], 
              'unit_price': row[3], 'quantity': row[4], 'amount': row[5]} 
             for row in c.fetchall()]
    conn.close()
    return jsonify(goods)

# 添加新货物
@app.route('/api/goods', methods=['POST'])
def add_good():
    data = request.json
    amount = data['unit_price'] * data['quantity']
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO goods (name, category, unit_price, quantity, amount)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['category'], data['unit_price'], data['quantity'], amount))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({'id': new_id, **data, 'amount': amount}), 201

# 删除货物
@app.route('/api/goods/<int:id>', methods=['DELETE'])
def delete_good(id):
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('DELETE FROM goods WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

# 清除所有货物
@app.route('/api/clear-goods', methods=['DELETE'])
def clear_goods():
    try:
        conn = sqlite3.connect('goods.db')
        c = conn.cursor()
        # 获取当前记录数
        c.execute('SELECT COUNT(*) FROM goods')
        count = c.fetchone()[0]
        # 清空表
        c.execute('DELETE FROM goods')
        conn.commit()
        conn.close()
        return jsonify({
            'message': '所有货物已清除',
            'count': count
        }), 200
    except Exception as e:
        return jsonify({'error': f'清除失败: {str(e)}'}), 500

# 导入Excel文件
@app.route('/api/import', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    try:
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 读取Excel文件
        df = pd.read_excel(filepath)
        
        # 重命名列以匹配所需格式
        column_mapping = {
            '产品信息': 'name',
            '实发数量': 'quantity',
            '发货日期': 'category'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 清理数量列中的非数字字符
        df['quantity'] = df['quantity'].astype(str).str.extract(r'(\d+)').astype(float)
        
        # 验证必要的列是否存在
        required_columns = ['name', 'quantity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'缺少必要的列: {", ".join(missing_columns)}'}), 400

        # 数据验证
        if df['name'].isnull().any():
            return jsonify({'error': '商品名称存在空值'}), 400

        # 删除数量为空或无效的行
        df = df.dropna(subset=['quantity'])
        
        if len(df) == 0:
            return jsonify({'error': '没有有效的数据行'}), 400

        # 按商品名称分组并合计数量
        df_grouped = df.groupby('name').agg({
            'quantity': 'sum',
            'category': 'first'  # 使用第一个出现的发货日期
        }).reset_index()

        # 添加单价和金额列（暂时设为0）
        df_grouped['unit_price'] = 0.0
        df_grouped['amount'] = 0.0

        # 将数据插入或更新数据库
        conn = sqlite3.connect('goods.db')
        cursor = conn.cursor()
        
        for _, row in df_grouped.iterrows():
            # 检查商品是否已存在
            cursor.execute('SELECT id, quantity FROM goods WHERE name = ?', (row['name'],))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # 更新现有记录
                new_quantity = existing_record[1] + row['quantity']
                cursor.execute('''
                    UPDATE goods 
                    SET quantity = ?, 
                        category = ?,
                        amount = unit_price * ?
                    WHERE id = ?
                ''', (new_quantity, row['category'], new_quantity, existing_record[0]))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO goods (name, category, unit_price, quantity, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['name'], row['category'], row['unit_price'], row['quantity'], row['amount']))

        conn.commit()
        conn.close()

        # 删除临时文件
        os.remove(filepath)

        return jsonify({'message': '导入成功', 'count': len(df_grouped)}), 200

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

# 配置Selenium
def setup_driver():
    """配置并初始化 Chrome WebDriver"""
    try:
        # 配置 Chrome 选项
        chrome_options = Options()
        
        # 基本设置
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')  # 禁用沙箱
        chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用共享内存
        chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
        chrome_options.add_argument('--disable-extensions')  # 禁用扩展
        chrome_options.add_argument('--disable-software-rasterizer')  # 禁用软件光栅化
        chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
        
        # 添加User-Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 使用 webdriver_manager 自动安装和管理 ChromeDriver
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                print(f"尝试安装 ChromeDriver (尝试 {retry_count + 1}/{max_retries})...")
                
                # 使用新版本的 ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                print(f"ChromeDriver 安装成功: {driver_path}")
                
                # 创建 Service 实例
                service = Service(driver_path)
                
                # 创建 WebDriver 实例
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 配置超时和其他设置
                driver.set_page_load_timeout(30)  # 页面加载超时
                driver.set_script_timeout(30)  # 脚本执行超时
                driver.implicitly_wait(10)  # 隐式等待
                
                print("WebDriver 初始化成功")
                return driver
                
            except Exception as e:
                last_error = str(e)
                print(f"尝试 {retry_count + 1} 失败: {last_error}")
                retry_count += 1
                
                if retry_count < max_retries:
                    wait_time = retry_count * 2
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    
                    # 检查是否是版本不匹配的错误
                    if "This version of ChromeDriver only supports Chrome version" in last_error:
                        print("检测到版本不匹配，尝试清除缓存后重试...")
                        try:
                            import shutil
                            cache_path = os.path.join(os.path.expanduser("~"), ".wdm")
                            if os.path.exists(cache_path):
                                shutil.rmtree(cache_path)
                                print("已清除 ChromeDriver 缓存")
                        except Exception as cache_error:
                            print(f"清除缓存失败: {str(cache_error)}")
        
        # 如果所有重试都失败
        error_msg = f"无法安装 ChromeDriver，已重试 {max_retries} 次。最后一次错误: {last_error}"
        print(error_msg)
        
        # 提供更详细的错误信息
        if "Connection refused" in str(last_error):
            raise Exception("网络连接被拒绝，请检查网络设置或代理配置")
        elif "timeout" in str(last_error).lower():
            raise Exception("网络连接超时，请检查网络状态")
        elif "SSL" in str(last_error):
            raise Exception("SSL证书验证失败，请检查网络设置")
        else:
            raise Exception(error_msg)
            
    except Exception as e:
        error_msg = str(e)
        print(f"浏览器初始化失败: {error_msg}")
        
        if "This version of ChromeDriver only supports Chrome version" in error_msg:
            raise Exception("ChromeDriver 版本与 Chrome 浏览器版本不匹配，请更新 Chrome 浏览器")
        elif "Chrome failed to start" in error_msg:
            raise Exception("Chrome 浏览器启动失败，请确保 Chrome 已正确安装")
        else:
            raise Exception(f"浏览器初始化失败: {error_msg}")

# 获取订单信息
@app.route('/api/fetch-orders', methods=['POST'])
def fetch_orders():
    driver = None
    try:
        # 获取用户选择的字段
        selected_fields = select_fields()
        if not selected_fields:
            return jsonify({'error': '未选择任何字段'}), 400
            
        # 获取字段对应的选择器
        selectors = get_field_selectors()
        
        # 初始化浏览器
        try:
            driver = setup_driver()
            if isinstance(driver, tuple):  # 检查是否是错误响应
                return driver
        except Exception as e:
            error_msg = str(e)
            print(f"浏览器初始化错误: {error_msg}")
            return handle_error(error_msg, fetch_orders)
        
        try:
            print("开始访问目标网页...")
            # 访问目标网页并等待加载
            driver.get("http://order.alittle-group.cn/web2/?code=041mIWll2WKMMe4Z0lll2LJexE4mIWle&state=1#/index")
            
            # 等待页面加载完成
            print("等待页面加载...")
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # 获取页面内容
            page_source = driver.page_source
            print(f"页面加载完成，内容长度: {len(page_source)}")
            
            # 查找订单元素
            print("查找订单元素...")
            orders = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.order-item'))
            )
            print(f"找到 {len(orders)} 个订单")
            
            if not orders:
                return jsonify({'error': '未找到订单数据，请检查页面是否正确加载'}), 404
            
            # 存储提取的数据
            extracted_data = []
            
            # 遍历订单元素并提取数据
            for index, order in enumerate(orders, 1):
                try:
                    print(f"处理第 {index} 个订单...")
                    order_data = {}
                    
                    # 只提取用户选择的字段
                    for field in selected_fields:
                        try:
                            element = WebDriverWait(order, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selectors[field]))
                            )
                            value = format_field_value(field, element.text)
                            order_data[field] = value
                        except Exception as field_error:
                            print(f"提取字段 {field} 失败: {str(field_error)}")
                            order_data[field] = "无数据"
                    
                    # 如果至少有一个字段有数据，则添加到结果中
                    if any(value != "无数据" for value in order_data.values()):
                        extracted_data.append(order_data)
                        
                        # 如果有数量和金额字段，则更新数据库
                        if 'name' in order_data and 'quantity' in order_data and order_data['quantity'] != "无数据":
                            try:
                                conn = sqlite3.connect('goods.db')
                                cursor = conn.cursor()
                                
                                # 检查商品是否已存在
                                cursor.execute('SELECT id, quantity FROM goods WHERE name = ?', (order_data['name'],))
                                existing_record = cursor.fetchone()
                                
                                quantity = order_data['quantity']
                                amount = order_data.get('amount', 0)
                                
                                if existing_record:
                                    # 更新现有记录
                                    new_quantity = existing_record[1] + quantity
                                    cursor.execute('''
                                        UPDATE goods 
                                        SET quantity = ?,
                                            amount = unit_price * ?
                                        WHERE id = ?
                                    ''', (new_quantity, new_quantity, existing_record[0]))
                                else:
                                    # 插入新记录
                                    unit_price = amount / quantity if amount and quantity else 0
                                    cursor.execute('''
                                        INSERT INTO goods (name, category, unit_price, quantity, amount)
                                        VALUES (?, ?, ?, ?, ?)
                                    ''', (order_data['name'], '自动导入', unit_price, quantity, amount))
                                
                                conn.commit()
                                print(f"数据库更新成功: {order_data['name']}")
                                
                            except Exception as db_error:
                                print(f"数据库操作失败: {str(db_error)}")
                            
                            finally:
                                conn.close()
                    
                except Exception as e:
                    print(f"处理订单时出错: {str(e)}")
                    continue
            
            if not extracted_data:
                return jsonify({'error': '未能成功提取任何订单数据'}), 500
            
            # 显示抓取结果
            display_results(extracted_data)
            
            return jsonify({
                'message': '订单获取成功',
                'count': len(extracted_data),
                'data': extracted_data
            }), 200
            
        except Exception as e:
            print(f"获取订单失败: {str(e)}")
            return handle_error(str(e), fetch_orders)
        
    except Exception as e:
        print(f"系统错误: {str(e)}")
        return handle_error(str(e), fetch_orders)
        
    finally:
        if driver:
            try:
                driver.quit()
                print("浏览器已关闭")
            except:
                print("关闭浏览器时出错")

def main():
    init_db()
    app.run(debug=True, use_reloader=True, reloader_type='stat')

if __name__ == '__main__':
    main() 