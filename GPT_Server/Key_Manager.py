import uuid
import json
import threading

class KeyManager:
    def __init__(self, file_path="keys.json"):
        self.file_path = file_path
        self.lock = threading.Lock()
        self.key_value_map = self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        return data

    def save_data(self):
        with self.lock:
            with open(self.file_path, "w") as file:
                json.dump(self.key_value_map, file)

    def add_key_value(self, key=None, value=0.0):
        with self.lock:
            if not key:
                key = str(uuid.uuid4())
            self.key_value_map[key] = value
            self.save_data()
        return key

    def remove_key(self, key):
        with self.lock:
            if key in self.key_value_map:
                del self.key_value_map[key]
                self.save_data()

    def check_key(self, key):
        with self.lock:
            return key in self.key_value_map

    def decrease_value(self, key, amount):
        with self.lock:
            if key not in self.key_value_map:
                return False,0

            if self.key_value_map[key] < amount:
                del self.key_value_map[key]
                return True,0

            self.key_value_map[key] -= amount
            
            self.save_data()
            return True,self.key_value_map[key]

# 使用示例
# key_manager = KeyManager()
# key = key_manager.add_key_value(value=100.0)
# key_manager.decrease_value(key, 50.0)
# key_manager.remove_key(key)
