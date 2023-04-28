import tkinter as tk
from tkinter import ttk

# 创建主窗口
class CHAT_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPT_GUI_2.0")
        self.geometry("800x600")
        self.create_widgets()

        self.settings_callback = None
        self.send_message_callback = None
        self.refresh_dialogue_callback = None
        self.restart_dialogue_callback = None

    # 创建并放置组件
    def create_widgets(self):
        # 创建左侧框架
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # 添加Temperature标签和输入框
        self.temperature_label = ttk.Label(self.left_frame, text="Temperature:")
        self.temperature_label.pack(side=tk.TOP, pady=10)
        self.temperature_entry = ttk.Entry(self.left_frame)
        self.temperature_entry.pack(side=tk.TOP)
        self.temperature_entry.insert(0, "0.5")  # 设置 temperature 默认值

        # 添加Max Tokens标签和输入框
        self.max_tokens_label = ttk.Label(self.left_frame, text="Max Tokens:")
        self.max_tokens_label.pack(side=tk.TOP, pady=10)
        self.max_tokens_entry = ttk.Entry(self.left_frame)
        self.max_tokens_entry.pack(side=tk.TOP)
        self.max_tokens_entry.insert(0, "300")  # 设置 temperature 默认值

        # 添加情景选择下拉框及其标签
        self.scenario_label = ttk.Label(self.left_frame, text="情景选择:")
        self.scenario_label.pack(side=tk.TOP, pady=10)
        self.scenario_combobox = ttk.Combobox(self.left_frame, values=["助手", "老师", "猫娘"])
        self.scenario_combobox.current(0)
        self.scenario_combobox.pack(side=tk.TOP)

        # 在左侧框架中添加设置
        self.setting_button = ttk.Button(self.left_frame, text="应用设置", command=self.settings)
        self.setting_button.pack(side=tk.TOP, pady=20)

        # 在左侧框架中添加
        self.setting_button = ttk.Button(self.left_frame, text="刷新", command=self.refresh_dialogue)
        self.setting_button.pack(side=tk.TOP, pady=10)

        # 添加对话计数器标签
        self.dialogue_counter_lable = ttk.Label(self.left_frame, text="建议对话次数 剩余：")
        self.dialogue_counter_lable.pack(side=tk.TOP, pady=10)

        # 在左侧框架中添加重启对话按钮
        self.setting_button = ttk.Button(self.left_frame, text="重启对话", command=self.restart_dialogue)
        self.setting_button.pack(side=tk.TOP, pady=10)

        # 创建对话框框架
        self.dialogue_frame = ttk.Frame(self)
        self.dialogue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建对话框文本区域
        self.dialogue_text = tk.Text(self.dialogue_frame, wrap=tk.WORD)
        self.dialogue_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 创建消息输入框和发送按钮
        self.message_entry = tk.Text(self.dialogue_frame, wrap=tk.WORD, height=3)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind('<Return>', self.handle_return)  # 绑定回车键事件
        self.send_button = ttk.Button(self.dialogue_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10)

    # 设置功能函数
    def settings(self) -> None:
        temperature = self.temperature_entry.get()
        max_tokens = self.max_tokens_entry.get()
        scenario = self.scenario_combobox.get()

        if self.settings_callback:
            self.settings_callback(float(temperature), int(max_tokens), scenario)
    
    def handle_return(self, event):
        self.send_message()
        return 'break'  # 阻止在文本输入框中插入换行符

    def send_message(self) -> None:
        message = self.message_entry.get("1.0", tk.END).strip()  # 获取多行文本框的内容
        if message:
            self.message_entry.delete("1.0", tk.END)  # 清空多行文本框的内容
            self.send_message_callback(message)
            self.dialogue_text.see(tk.END)  # 让对话框滚动到最下部以显示最新信息

    def insert_message(self, message: str) -> None:
        self.dialogue_text.insert(tk.END, message + "\n\n")
        self.dialogue_text.see(tk.END)  # 让对话框滚动到最下部以显示最新信息
    
    def refresh_dialogue(self) -> None:
        self.refresh_dialogue_callback()
    
    def restart_dialogue(self) -> None:
        self.restart_dialogue_callback()
    
    def clear_dialogue(self) -> None:
        self.dialogue_text.delete("1.0", tk.END)

    def update_dialogue_counter_text(self, new_text: str, color: str = "black"):
        self.dialogue_counter_lable.config(text=new_text,foreground=color)


# # 运行程序
# if __name__ == "__main__":
#     chat_gui = ChatGUI()
#     chat_gui.mainloop()





