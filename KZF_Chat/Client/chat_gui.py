import tkinter as tk
from tkinter import ttk

# 创建主窗口
class ChatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("对话程序")
        self.geometry("800x600")
        self.create_widgets()

    # 创建并放置组件
    def create_widgets(self):
        # 创建左侧框架
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # 在左侧框架中添加设置和调参按钮
        self.setting_button = ttk.Button(self.left_frame, text="设置", command=self.settings)
        self.setting_button.pack(side=tk.TOP, pady=10)

        self.adjust_params_button = ttk.Button(self.left_frame, text="调参", command=self.adjust_params)
        self.adjust_params_button.pack(side=tk.TOP, pady=10)

        # 添加Temperature标签和输入框
        self.temperature_label = ttk.Label(self.left_frame, text="Temperature:")
        self.temperature_label.pack(side=tk.TOP, pady=10)
        self.temperature_entry = ttk.Entry(self.left_frame)
        self.temperature_entry.pack(side=tk.TOP, pady=10)

        # 添加Max Tokens标签和输入框
        self.max_tokens_label = ttk.Label(self.left_frame, text="Max Tokens:")
        self.max_tokens_label.pack(side=tk.TOP, pady=10)
        self.max_tokens_entry = ttk.Entry(self.left_frame)
        self.max_tokens_entry.pack(side=tk.TOP, pady=10)

        # 添加情景选择下拉框及其标签
        self.scenario_label = ttk.Label(self.left_frame, text="情景选择:")
        self.scenario_label.pack(side=tk.TOP, pady=10)
        self.scenario_combobox = ttk.Combobox(self.left_frame, values=["助手", "翻译器"])
        self.scenario_combobox.current(0)
        self.scenario_combobox.pack(side=tk.TOP, pady=10)

        # 创建对话框框架
        self.dialogue_frame = ttk.Frame(self)
        self.dialogue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建对话框文本区域
        self.dialogue_text = tk.Text(self.dialogue_frame, wrap=tk.WORD)
        self.dialogue_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 创建消息输入框和发送按钮
        self.message_entry = ttk.Entry(self.dialogue_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.send_button = ttk.Button(self.dialogue_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10)

    # 设置功能函数
    def settings(self):
        print("打开设置")

    # 调参功能函数
    def adjust_params(self):
        print("进行参数调整")

    # 发送消息功能函数
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.dialogue_text.insert(tk.END, "用户: " + message + "\n")
            self.message_entry.delete(0, tk.END)

# 运行程序
if __name__ == "__main__":
    chat_gui = ChatGUI()
    chat_gui.mainloop()

