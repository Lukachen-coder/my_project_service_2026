import csv
import json
import os

class AddressDB:
    def __init__(self, file_path='../data/addr.csv'):
        self.file_path = file_path
        # 确保文件存在
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'user_id', 'name', 'phone', 'province', 'city', 'district', 'address', 'is_default'])
    
    def get_all(self, user_id):
        """获取用户的所有地址"""
        addresses = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        addresses.append({
                            'id': row['id'],
                            'user_id': row['user_id'],
                            'name': row['name'],
                            'phone': row['phone'],
                            'province': row['province'],
                            'city': row['city'],
                            'district': row['district'],
                            'address': row['address'],
                            'is_default': row['is_default'] == '1'
                        })
        except Exception as e:
            print(f"Error getting addresses: {e}")
        return addresses
    
    def get_by_id(self, address_id, user_id):
        """根据ID获取地址"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id'] == address_id and row['user_id'] == user_id:
                        return {
                            'id': row['id'],
                            'user_id': row['user_id'],
                            'name': row['name'],
                            'phone': row['phone'],
                            'province': row['province'],
                            'city': row['city'],
                            'district': row['district'],
                            'address': row['address'],
                            'is_default': row['is_default'] == '1'
                        }
        except Exception as e:
            print(f"Error getting address: {e}")
        return None
    
    def add(self, user_id, name, phone, province, city, district, address, is_default=False):
        """添加新地址"""
        try:
            # 生成新ID
            addresses = self.get_all(user_id)
            new_id = str(len(addresses) + 1) if addresses else '1'
            
            # 如果设置为默认地址，将其他地址设置为非默认
            if is_default:
                self._update_default(user_id, None)
            
            # 写入新地址
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([new_id, user_id, name, phone, province, city, district, address, '1' if is_default else '0'])
            return new_id
        except Exception as e:
            print(f"Error adding address: {e}")
            return None
    
    def update(self, address_id, user_id, name, phone, province, city, district, address, is_default=False):
        """更新地址"""
        try:
            rows = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['id'] == address_id and row['user_id'] == user_id:
                        # 更新地址信息
                        row['name'] = name
                        row['phone'] = phone
                        row['province'] = province
                        row['city'] = city
                        row['district'] = district
                        row['address'] = address
                        row['is_default'] = '1' if is_default else '0'
                    rows.append(row)
            
            # 如果设置为默认地址，将其他地址设置为非默认
            if is_default:
                for i, row in enumerate(rows):
                    if row['user_id'] == user_id and row['id'] != address_id:
                        rows[i]['is_default'] = '0'
            
            # 写回文件
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Error updating address: {e}")
            return False
    
    def delete(self, address_id, user_id):
        """删除地址"""
        try:
            rows = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if not (row['id'] == address_id and row['user_id'] == user_id):
                        rows.append(row)
            
            # 写回文件
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Error deleting address: {e}")
            return False
    
    def _update_default(self, user_id, default_id):
        """更新默认地址"""
        try:
            rows = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['user_id'] == user_id:
                        row['is_default'] = '1' if row['id'] == default_id else '0'
                    rows.append(row)
            
            # 写回文件
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as e:
            print(f"Error updating default address: {e}")
