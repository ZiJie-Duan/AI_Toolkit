import time
import pyperclip
import tkinter as tk
from tkinter import ttk
import keyboard
import ctypes
from ctypes import wintypes
import winsound

from TCP_Client import TCPClient
from setting import SETTING
from StoryBoard import Memo, StoryBoard
from threading import Thread


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def query_mouse_position():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def press_ctrl_c():
    keyboard.press('ctrl+alt+b')
    keyboard.release('ctrl+alt+b')

def translate_text(text,set,tcp_client,story_board):

    messages = story_board.get_dialogue_history()
    messages.append({"role": "user", "content": text})

    data = {"key": set.kzf_key,
            "storyboard": messages,
            "temperature": 0.5,
            "max_tokens": 800}
    
    try:
        ai_response = tcp_client.start(data)
    except Exception as e:
        return "AI服务器连接失败，请联系开发者"

    if ai_response["info"] == "success":
        reply = ai_response["reply"]
    elif ai_response["info"] == "key_error":
        reply = "程序秘钥错误，请联系开发者，更新程序"

    return reply

def close_window(window):
    window.destroy()


def main():
    
    set = SETTING()

    memo = Memo(set.memo_file)
    storyboard = StoryBoard(memo,set.back_ground)
    tcp_client = TCPClient(server_address=(set.host, set.port))
    
    def handle_it(storyboard, tcp_client, set):

        def on_key_release(e):
            if e.keysym == 'Escape':
                close_window(window)

            try: 
                print("快捷键触发")

                press_ctrl_c()

                time.sleep(0.1)

                # 从剪切板读取选中的文本
                selected_text = pyperclip.paste()
                print("选中文本：", selected_text)

                winsound.MessageBeep()

                # 如果剪切板为空或只有空格，不执行翻译
                if not selected_text.strip():
                    print("没有选中任何文本")
                    return

                # 翻译文本
                translated_text = translate_text(selected_text,set,tcp_client,storyboard)
                print("AI翻译：", translated_text)
                mouse_x, mouse_y = query_mouse_position()

                pyperclip.copy(translated_text)

                window = tk.Tk()
                window.title("AI翻译")
                window.attributes('-topmost', True)  # 保持窗口在最前端
                window.bind('<KeyRelease>', on_key_release)
                
                label = ttk.Label(window, text=translated_text, wraplength=380, justify="left")
                label.pack(padx=20, pady=20)
                button = ttk.Button(window, text="关闭", command=lambda: close_window(window))
                button.pack(pady=10)

                window.update_idletasks()
                window_width = window.winfo_width()
                window_height = window.winfo_height()

                window.geometry(f"{window_width}x{window_height}+{mouse_x + 10}+{mouse_y - window_height // 2}")
                window.mainloop()
                
            except Exception as e:
                print("翻译失败：", e)
                return

    while True:
        # 等待特定快捷键，例如 'ctrl+alt+t'
        print("等待全局快捷键 (如：Ctrl+B)...")
        keyboard.wait('ctrl+b')

        thread_s = Thread(target=handle_it, args=(storyboard, tcp_client, set))
        thread_s.start()
        
if __name__ == "__main__":
    main()
