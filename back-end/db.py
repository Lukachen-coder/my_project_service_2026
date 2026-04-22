import csv
import os

class Database:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password'])
    
    def get_all_users(self):
        users = []
        with open(self.file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
        return users
    
    def get_user(self, username):
        with open(self.file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username:
                    return row
        return None
    
    def add_user(self, username, password):
        if self.get_user(username):
            return False
        with open(self.file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        return True
    
    def update_user(self, username, new_password):
        users = self.get_all_users()
        updated = False
        with open(self.file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
            for user in users:
                if user['username'] == username:
                    writer.writerow([username, new_password])
                    updated = True
                else:
                    writer.writerow([user['username'], user['password']])
        return updated
    
    def delete_user(self, username):
        users = self.get_all_users()
        deleted = False
        with open(self.file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
            for user in users:
                if user['username'] != username:
                    writer.writerow([user['username'], user['password']])
                else:
                    deleted = True
        return deleted
