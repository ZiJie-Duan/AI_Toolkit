import os
import shutil

def remove_pycache(directory):
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            if d == "__pycache__":
                pycache_path = os.path.join(root, d)
                print(f"删除: {pycache_path}")
                shutil.rmtree(pycache_path)

if __name__ == "__main__":
    directory = input("请输入要搜索的目录路径: ")
    remove_pycache(directory)
    print("完成删除所有__pycache__文件夹及其子文件。")
    input("按任意键退出。")
