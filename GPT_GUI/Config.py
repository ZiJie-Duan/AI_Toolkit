import configparser
from typing import Any
from Exception_Handler import exception_handler

class Config:

    def __init__(self, path='config.ini'):
        self.config = configparser.ConfigParser()
        self.path = path
        self.read(path)

    def __call__(self, section_key) -> Any:
        return self.get_value(section_key)

    @exception_handler
    def read(self, path):
        self.config.read(path, encoding='utf-8')

    @exception_handler
    def get_value(self, config_string: str) -> Any:
        section, key = config_string.split('.')
        value = self.config.get(section, key)

        # 尝试将值转换为布尔型
        try:
            return self.config.getboolean(section, key)
        except ValueError:
            pass

        # 尝试将值转换为整型
        try:
            return self.config.getint(section, key)
        except ValueError:
            pass

        # 尝试将值转换为浮点型
        try:
            return self.config.getfloat(section, key)
        except ValueError:
            pass

        # 如果以上尝试都失败，则返回字符串值
        return value
    

    @exception_handler
    def set(self, section, key, value: Any):
        if not self.config.has_section(section):
            self.add_section(section)
        
        # 将值转换为字符串
        value_str = str(value)
        
        self.config.set(section, key, value_str)
        self.save()

    @exception_handler
    def add_section(self, section):
        self.config.add_section(section)

    @exception_handler
    def save(self):
        with open(self.path, 'w') as configfile:
            self.config.write(configfile)


# 示例用法
# cf = Config()
# print(cf.get('database', 'host'))
# cf.set('database', 'host', 'ababa')
# cf.set('23', '23', '23232')
# cf.save()
