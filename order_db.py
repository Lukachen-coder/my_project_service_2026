import csv
import json
import os
from datetime import datetime

class OrderDB:
    def __init__(self, file_path):
        self.file_path = file_path
        # 确保文件存在
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['order_id', 'user_id', 'service_type', 'status', 'created_at', 'updated_at', 'details'])
    
    def get_all_orders(self):
        orders = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 解析details字段为字典
                    if row.get('details'):
                        try:
                            row['details'] = json.loads(row['details'])
                        except Exception as e:
                            print(f"解析订单详情失败: {e}")
                            # 如果解析失败，将details设置为空字典
                            row['details'] = {}
                    else:
                        row['details'] = {}
                    orders.append(row)
        except Exception as e:
            print(f"获取订单列表失败: {e}")
        return orders
    
    def get_order(self, order_id):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('order_id') == order_id:
                        if row.get('details'):
                            row['details'] = json.loads(row['details'])
                        return row
        except Exception as e:
            print(f"获取订单失败: {e}")
        return None
    
    def add_order(self, user_id, service_type, details):
        try:
            # 生成订单ID
            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            # 获取当前时间
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 初始状态为待处理
            status = 'pending'
            # 将details转换为JSON字符串
            details_json = json.dumps(details, ensure_ascii=False)
            
            # 写入订单
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([order_id, user_id, service_type, status, now, now, details_json])
            
            return order_id
        except Exception as e:
            print(f"添加订单失败: {e}")
            return None
    
    def update_order(self, order_id, **kwargs):
        try:
            orders = self.get_all_orders()
            updated = False
            
            # 更新订单
            for order in orders:
                if order.get('order_id') == order_id:
                    # 更新字段
                    for key, value in kwargs.items():
                        if key == 'details':
                            order[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            order[key] = value
                    # 更新时间
                    order['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    break
            
            # 写回文件
            if updated:
                with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['order_id', 'user_id', 'service_type', 'status', 'created_at', 'updated_at', 'details'])
                    for order in orders:
                        row = [
                            order.get('order_id'),
                            order.get('user_id'),
                            order.get('service_type'),
                            order.get('status'),
                            order.get('created_at'),
                            order.get('updated_at'),
                            json.dumps(order.get('details'), ensure_ascii=False) if isinstance(order.get('details'), dict) else order.get('details')
                        ]
                        writer.writerow(row)
                return True
            return False
        except Exception as e:
            print(f"更新订单失败: {e}")
            return False
    
    def delete_order(self, order_id):
        try:
            orders = self.get_all_orders()
            filtered_orders = [order for order in orders if order.get('order_id') != order_id]
            
            # 写回文件
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['order_id', 'user_id', 'service_type', 'status', 'created_at', 'updated_at', 'details'])
                for order in filtered_orders:
                    row = [
                        order.get('order_id'),
                        order.get('user_id'),
                        order.get('service_type'),
                        order.get('status'),
                        order.get('created_at'),
                        order.get('updated_at'),
                        json.dumps(order.get('details'), ensure_ascii=False) if isinstance(order.get('details'), dict) else order.get('details')
                    ]
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"删除订单失败: {e}")
            return False
    
    def get_user_orders(self, user_id):
        orders = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('user_id') == user_id:
                        if row.get('details'):
                            row['details'] = json.loads(row['details'])
                        orders.append(row)
        except Exception as e:
            print(f"获取用户订单失败: {e}")
        return orders
