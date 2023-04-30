import threading
import subprocess

def run_file(file):
    subprocess.run(["python", file])

files = ["chat.py", "key_test.py", "login.py"]
threads = []

for file in files:
    thread = threading.Thread(target=run_file, args=(file,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
