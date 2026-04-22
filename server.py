import json
import csv
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import traceback
import signal
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 自动获取项目根目录（back-end目录的父目录）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # back-end目录
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)  # 项目根目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FRONT_END_DIR = os.path.join(PROJECT_ROOT, 'front-end')

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            logging.info(f'Received GET request: {self.path}')
            
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            
            if path.startswith('/api/'):
                if path == '/api/users':
                    self.handle_get_users()
                elif path == '/api/orders':
                    self.handle_get_orders()
                elif path == '/api/addresses':
                    self.handle_get_addresses()
                else:
                    self.send_error(404, 'API endpoint not found')
            else:
                self.handle_static_file()
        except Exception as e:
            logging.error(f'Error in do_GET: {e}\n{traceback.format_exc()}')
            self.send_error(500, 'Internal server error')

    def do_POST(self):
        try:
            # 处理 API 请求
            if self.path.startswith('/api/'):
                if self.path == '/api/register':
                    self.handle_register()
                elif self.path == '/api/login':
                    self.handle_login()
                elif self.path == '/api/order':
                    self.handle_order()
                elif self.path == '/api/address' or self.path == '/api/addresses':
                    self.handle_address()
                else:
                    self.send_error(404, 'API endpoint not found')
            else:
                self.send_error(404, 'Not found')
        except Exception as e:
            logging.error(f'Error in do_POST: {e}\n{traceback.format_exc()}')
            self.send_error(500, 'Internal server error')

    def do_DELETE(self):
        try:
            # 处理 API 请求
            if self.path.startswith('/api/address/'):
                self.handle_delete_address()
            elif self.path.startswith('/api/order/'):
                self.handle_cancel_order()
            else:
                self.send_error(404, 'API endpoint not found')
        except Exception as e:
            logging.error(f'Error in do_DELETE: {e}\n{traceback.format_exc()}')
            self.send_error(500, 'Internal server error')

    def do_OPTIONS(self):
        # 处理 CORS 预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def handle_static_file(self):
        # 处理静态文件请求
        try:
            # 处理路径
            path = self.path
            
            # 移除查询参数
            if '?' in path:
                path = path.split('?')[0]
            
            # 处理根路径
            if path == '/':
                path = '/login.html'
            
            # 确保路径以 '/' 开头
            if not path.startswith('/'):
                path = '/' + path
            
            # 提取文件名
            filename = path[1:]  # 移除开头的 '/' 符号
            
            # 构建完整路径
            full_path = os.path.join(FRONT_END_DIR, filename)
            
            # 检查文件是否存在
            if not os.path.exists(full_path):
                self.send_error(404, f'File not found: {filename}')
                return
            
            # 检查是否是文件
            if not os.path.isfile(full_path):
                self.send_error(404, f'File not found: {filename}')
                return
            
            # 读取文件内容
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # 设置Content-Type
            if filename.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif filename.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
            elif filename.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
            else:
                content_type = 'application/octet-stream'
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f'File not found')
        except Exception as e:
            logging.error(f'Error serving static file: {e}')
            self.send_error(500, 'Internal server error')

    def handle_register(self):
        # 处理注册请求
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)

            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            if not username or not password:
                self.send_simple_response({'success': False, 'message': '用户名和密码不能为空'})
                return

            # 检查用户是否已存在
            users_file = os.path.join(DATA_DIR, 'users.csv')
            if os.path.exists(users_file):
                with open(users_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['username'] == username:
                            self.send_simple_response({'success': False, 'message': '用户名已存在'})
                            return

            # 确保 data 目录存在
            os.makedirs(DATA_DIR, exist_ok=True)

            # 写入用户数据
            with open(users_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['username', 'password']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow({'username': username, 'password': password})

            self.send_simple_response({'success': True, 'message': '注册成功'})
        except Exception as e:
            logging.error(f'Error in handle_register: {e}')
            self.send_simple_response({'success': False, 'message': '注册失败'})

    def handle_login(self):
        # 处理登录请求
        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = urllib.parse.parse_qs(post_data)
            else:
                params = {}

            # 获取用户名和密码
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            # 验证输入
            if not username or not password:
                self.send_simple_response({'success': False, 'message': '用户名和密码不能为空'})
                return

            # 检查用户是否存在
            users_file = os.path.join(DATA_DIR, 'users.csv')
            if not os.path.exists(users_file):
                self.send_simple_response({'success': False, 'message': '用户名或密码错误'})
                return

            # 验证用户凭据
            found = False
            try:
                with open(users_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    # 跳过表头
                    header = next(reader, None)
                    if header:
                        for row in reader:
                            if len(row) >= 2:
                                if row[0] == username and row[1] == password:
                                    found = True
                                    break
            except Exception as e:
                logging.error(f'Error reading users file: {e}')

            # 返回结果
            if found:
                self.send_simple_response({'success': True, 'message': '登录成功'})
            else:
                self.send_simple_response({'success': False, 'message': '用户名或密码错误'})
        except Exception as e:
            logging.error(f'Error in handle_login: {e}')
            self.send_simple_response({'success': False, 'message': '登录失败'})

    def handle_order(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            order_data = json.loads(post_data)

            os.makedirs(DATA_DIR, exist_ok=True)

            orders_file = os.path.join(DATA_DIR, 'orders.csv')
            existing_orders = []
            if os.path.exists(orders_file):
                with open(orders_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_orders = list(reader)
            order_id = str(len(existing_orders) + 1)

            with open(orders_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'user_id', 'service_type', 'details', 'status', 'timestamp']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow({
                    'id': order_id,
                    'user_id': order_data.get('user_id', ''),
                    'service_type': order_data.get('service_type', ''),
                    'details': json.dumps(order_data.get('details', {})),
                    'status': 'pending',
                    'timestamp': order_data.get('timestamp', '')
                })

            self.send_simple_response({'success': True, 'message': '订单提交成功'})
        except Exception as e:
            logging.error(f'Error in handle_order: {e}')
            self.send_simple_response({'success': False, 'message': '订单提交失败'})

    def handle_address(self):
        # 处理地址请求
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            address_data = json.loads(post_data)

            # 确保 data 目录存在
            os.makedirs(DATA_DIR, exist_ok=True)

            # 生成地址 ID
            addresses_file = os.path.join(DATA_DIR, 'addr.csv')
            existing_addresses = []
            fieldnames = ['id', 'user_id', 'name', 'phone', 'province', 'city', 'district', 'address', 'is_default']
            
            # 读取现有地址
            if os.path.exists(addresses_file):
                with open(addresses_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    existing_addresses = list(reader)
            
            # 检查是否是编辑操作
            address_id = address_data.get('id')
            is_edit = address_id is not None
            
            if not is_edit:
                # 新增地址
                address_id = str(len(existing_addresses) + 1)
            
            # 如果设置为默认地址，需要将其他地址的默认状态设置为0
            is_default = address_data.get('is_default', '0')
            if is_default == '1' and existing_addresses:
                for addr in existing_addresses:
                    addr['is_default'] = '0'

            # 创建或更新地址对象
            address_obj = {
                'id': address_id,
                'user_id': address_data.get('user_id', ''),
                'name': address_data.get('name', ''),
                'phone': address_data.get('phone', ''),
                'province': address_data.get('province', ''),
                'city': address_data.get('city', ''),
                'district': address_data.get('district', ''),
                'address': address_data.get('address', ''),
                'is_default': is_default
            }

            if is_edit:
                # 更新现有地址
                updated = False
                for i, addr in enumerate(existing_addresses):
                    if addr['id'] == address_id:
                        existing_addresses[i] = address_obj
                        updated = True
                        break
                if not updated:
                    existing_addresses.append(address_obj)
            else:
                # 将新地址添加到现有地址列表
                existing_addresses.append(address_obj)

            # 重新写入所有地址（包括新地址）
            with open(addresses_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for addr in existing_addresses:
                    writer.writerow(addr)

            self.send_simple_response({'success': True, 'message': '地址更新成功' if is_edit else '地址添加成功'})
        except Exception as e:
            logging.error(f'Error in handle_address: {e}')
            self.send_simple_response({'success': False, 'message': '地址添加失败'})

    def handle_delete_address(self):
        # 处理删除地址请求
        try:
            # 从路径中获取地址ID
            address_id = self.path.split('/api/address/')[1]
            
            addresses_file = os.path.join(DATA_DIR, 'addr.csv')
            if not os.path.exists(addresses_file):
                self.send_simple_response({'success': False, 'message': '地址不存在'})
                return

            # 读取所有地址，排除要删除的地址
            remaining_addresses = []
            with open(addresses_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['id'] != address_id:
                        remaining_addresses.append(row)

            # 重新写入文件
            with open(addresses_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for addr in remaining_addresses:
                    writer.writerow(addr)

            self.send_simple_response({'success': True, 'message': '地址删除成功'})
        except Exception as e:
            logging.error(f'Error in handle_delete_address: {e}')
            self.send_simple_response({'success': False, 'message': '地址删除失败'})

    def handle_get_users(self):
        # 处理获取用户列表请求
        try:
            users = []
            users_file = os.path.join(DATA_DIR, 'users.csv')
            if os.path.exists(users_file):
                with open(users_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        users.append(row)
            self.send_simple_response({'success': True, 'data': users})
        except Exception as e:
            logging.error(f'Error in handle_get_users: {e}')
            self.send_simple_response({'success': False, 'message': '获取用户列表失败'})

    def handle_get_orders(self):
        try:
            orders = []
            orders_file = os.path.join(DATA_DIR, 'orders.csv')
            
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            user_id = query_params.get('user_id', [''])[0]
            
            if os.path.exists(orders_file):
                with open(orders_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if user_id and row.get('user_id') != user_id:
                            continue
                        try:
                            row['details'] = json.loads(row['details'])
                        except:
                            row['details'] = {}
                        orders.append(row)
            self.send_simple_response({'success': True, 'data': orders})
        except Exception as e:
            logging.error(f'Error in handle_get_orders: {e}')
            self.send_simple_response({'success': False, 'message': '获取订单列表失败'})

    def handle_get_addresses(self):
        try:
            addresses = []
            addresses_file = os.path.join(DATA_DIR, 'addr.csv')
            
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            user_id = query_params.get('user_id', [''])[0]
            
            if os.path.exists(addresses_file):
                with open(addresses_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if user_id and row.get('user_id') != user_id:
                            continue
                        addresses.append(row)
            self.send_simple_response({'success': True, 'data': addresses})
        except Exception as e:
            logging.error(f'Error in handle_get_addresses: {e}')
            self.send_simple_response({'success': False, 'message': '获取地址列表失败'})

    def handle_cancel_order(self):
        # 处理取消订单请求
        try:
            # 从路径中获取订单ID
            order_id = self.path.split('/api/order/')[1]
            
            orders_file = os.path.join(DATA_DIR, 'orders.csv')
            if not os.path.exists(orders_file):
                self.send_simple_response({'success': False, 'message': '订单不存在'})
                return

            # 读取所有订单，排除要取消的订单
            remaining_orders = []
            with open(orders_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    # 检查是使用 id 还是 order_id 字段
                    row_id = row.get('id', row.get('order_id', ''))
                    if row_id != order_id:
                        remaining_orders.append(row)

            # 重新写入文件
            with open(orders_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for order in remaining_orders:
                    writer.writerow(order)

            self.send_simple_response({'success': True, 'message': '订单取消成功'})
        except Exception as e:
            logging.error(f'Error in handle_cancel_order: {e}')
            self.send_simple_response({'success': False, 'message': '订单取消失败'})

    def send_simple_response(self, data):
        # 发送简单的 JSON 响应
        try:
            # 构造响应内容并编码为字节
            response_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(response_bytes)))
            self.end_headers()
            # 发送数据
            self.wfile.write(response_bytes)
            self.wfile.flush()
        except Exception as e:
            logging.error(f'Error in send_simple_response: {e}')
            # 如果发送失败，发送一个简单的文本响应
            error_msg = b'Internal server error'
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(error_msg)))
            self.end_headers()
            self.wfile.write(error_msg)
            self.wfile.flush()

    def handle(self):
        # 重写 handle 方法，捕获连接异常
        try:
            super().handle()
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
            # 忽略连接中断错误
            logging.warning(f'Connection error: {e}')
        except Exception as e:
            # 记录其他错误
            logging.error(f'Error in handle: {e}\n{traceback.format_exc()}')

    def finish(self):
        # 重写 finish 方法，捕获连接异常
        try:
            super().finish()
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
            # 忽略连接中断错误
            logging.warning(f'Connection error in finish: {e}')
        except Exception as e:
            # 记录其他错误
            logging.error(f'Error in finish: {e}\n{traceback.format_exc()}')

def signal_handler(sig, frame):
    # 处理 SIGINT 信号（Ctrl+C）
    logging.info('Server shutting down...')
    server.shutdown()
    server.server_close()
    logging.info('Server stopped')
    sys.exit(0)

if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    # 调试：打印路径信息
    print(f'当前工作目录: {os.getcwd()}')
    print(f'项目根目录(PROJECT_ROOT): {PROJECT_ROOT}')
    print(f'前端目录: {FRONT_END_DIR}')
    print(f'前端目录存在: {os.path.exists(FRONT_END_DIR)}')
    print(f'index.html存在: {os.path.exists(os.path.join(FRONT_END_DIR, "index.html"))}')
    print(f'数据目录: {DATA_DIR}')

    # 启动服务器
    host = '0.0.0.0'  # 固定为0.0.0.0，确保外部可以访问
    # 优先读取系统环境变量PORT，默认值为8001
    port = int(os.environ.get('PORT', 8001))
    server = HTTPServer((host, port), MyRequestHandler)

    # 打印启动信息
    print('\n' + '=' * 60)
    print('上门服务系统服务器启动成功！')
    print('=' * 60)
    print(f'服务器地址: http://{host}:{port}')
    print(f'前端页面: http://{host}:{port}')
    print(f'API 接口: http://{host}:{port}/api')
    print(f'项目根目录: {PROJECT_ROOT}')
    print(f'数据目录: {DATA_DIR}')
    print('=' * 60)
    print('按 Ctrl+C 关闭服务器')
    print('=' * 60 + '\n')

    # 启动服务器
    try:
        server.serve_forever()
    except Exception as e:
        logging.error(f'Error starting server: {e}')
    finally:
        server.server_close()