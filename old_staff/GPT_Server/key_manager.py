from module.Config import Config
from module.Key_Manager import KeyManager
import click
from uuid import uuid4
import sys

#CONFIG_FILE = "/www/GPT_python_v3/server_config.ini"
CONFIG_FILE = "server_config.ini"

@click.option('--add', '-a', help='add a new key', is_flag=True)
@click.option('--delete', '-d', help='delete a key', is_flag=True)
@click.option('--change', '-c', help='change value of key', is_flag=True)
@click.option('--ls', '-l', help='list all keys', is_flag=True)
@click.argument('key', type=str, required=False) # n is None
@click.argument('value', type=int, required=False)
# if key is not None, value is not enabled
@click.argument('num', type=str, required=False)
def key(add, delete, ls, key=None, value=2000, num=1):
    cfg = Config(path = CONFIG_FILE)
    keymanager = KeyManager(cfg("USERKEY.file_path"))
    if add:
        print("add key-value")
        print("ID   KEY  -VALUE: ", value)
        if key == 'n':
            for i in range(int(num)):
                key = uuid4().hex
                keymanager.add_key_value(key=key, value=value)
                print(uuid4().hex, key)
        else:
            keymanager.add_key_value(key=key, value=value)
            print(uuid4().hex, key)
    elif delete:
        if key is None or key == 'n':
            print("Please enter the correct arguments")
            return
        keymanager.remove_key(key)
        print("delete key")
        print(key)
    elif ls:
        print("list all keys\n")
        kv = keymanager.get_all_keys_value()
        print("-"*50)
        for k, v in kv:
            print(f"{k:<40s} : {v:<10d}")
        print("-"*50)
    else:
        print("Please enter the correct command")


# Add the following line to handle command line arguments with Click library
key = click.command()(key)

if len(sys.argv) == 1:
    print("Usage: python key_manager.py [OPTIONS] [ARGUMENTS]")
    print("Try 'python key_manager.py --help' for help.")
else:
    key()
