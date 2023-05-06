import tkinter as tk
from tkinter import ttk

# 创建主窗口
class CHAT_GUI(tk.Tk):
    def __init__(self,
                title="UI_GPT",
                geometry="800x600",
                selected_scenario = None,
                selected_model = None,
                scenario = [],
                models = [],
                temperature = "0.5",
                max_tokens = "300",
                user_key = "",
                settings_callback=None,
                send_message_callback=None,
                refresh_dialogue_callback=None,
                restart_dialogue_callback=None
                ):
        
        super().__init__()
        self.title(title)
        self.geometry(geometry)

        self.selected_model = selected_model
        self.selected_scenario = selected_scenario
        self.models = models
        self.scenario = scenario
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.user_key = user_key

        self.settings_callback = settings_callback
        self.send_message_callback = send_message_callback
        self.refresh_dialogue_callback = refresh_dialogue_callback
        self.restart_dialogue_callback = restart_dialogue_callback

        self.create_widgets()

    # 创建并放置组件
    def create_widgets(self):
        
        # 创建左侧框架
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        # 在此处添加模型选择下拉框及其标签
        self.model_label = ttk.Label(self.left_frame, text="选择模型:")
        self.model_label.pack(side=tk.TOP, pady=10)
        self.model_combobox = ttk.Combobox(self.left_frame, values=self.models)
        self.model_combobox.set(self.selected_model)
        self.model_combobox.pack(side=tk.TOP)

        # 添加Temperature标签和输入框
        self.temperature_label = ttk.Label(self.left_frame, text="Temperature:")
        self.temperature_label.pack(side=tk.TOP, pady=10)
        self.temperature_entry = ttk.Entry(self.left_frame)
        self.temperature_entry.pack(side=tk.TOP)
        self.temperature_entry.insert(0, self.temperature)  # 设置 temperature 默认值

        # 添加Max Tokens标签和输入框
        self.max_tokens_label = ttk.Label(self.left_frame, text="Max Tokens:")
        self.max_tokens_label.pack(side=tk.TOP, pady=10)
        self.max_tokens_entry = ttk.Entry(self.left_frame)
        self.max_tokens_entry.pack(side=tk.TOP)
        self.max_tokens_entry.insert(0, self.max_tokens)  # 设置 temperature 默认值

        # 添加情景选择下拉框及其标签
        self.scenario_label = ttk.Label(self.left_frame, text="情景选择:")
        self.scenario_label.pack(side=tk.TOP, pady=10)
        self.scenario_combobox = ttk.Combobox(self.left_frame, values=self.scenario)
        self.scenario_combobox.set(self.selected_scenario)
        self.scenario_combobox.pack(side=tk.TOP)

        # 添加 user key 标签和输入框
        self.user_key_label = ttk.Label(self.left_frame, text="用户密钥:")
        self.user_key_label.pack(side=tk.TOP, pady=10)
        self.user_key_entry = ttk.Entry(self.left_frame)
        self.user_key_entry.pack(side=tk.TOP)
        self.user_key_entry.insert(0, self.user_key)  # 设置 user key 默认值

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
    def settings(self, hidden=False) -> None:
        model = self.model_combobox.get()
        temperature = self.temperature_entry.get()
        max_tokens = self.max_tokens_entry.get()
        scenario = self.scenario_combobox.get()
        user_key = self.user_key_entry.get()

        return self.settings_callback( str(model),
                                    float(temperature), 
                                    int(max_tokens),
                                    scenario,
                                    user_key,
                                    hidden=hidden)
    
    def handle_return(self, event):
        self.send_message()
        return 'break'  # 阻止在文本输入框中插入换行符

    def send_message(self) -> None:
        if self.settings(hidden=True):
            message = self.message_entry.get("1.0", tk.END).strip()  # 获取多行文本框的内容
            if message:
                self.message_entry.delete("1.0", tk.END)  # 清空多行文本框的内容
                self.send_message_callback(message)
                self.dialogue_text.see(tk.END)  # 让对话框滚动到最下部以显示最新信息

    def insert_message(self, message: str, enter=True) -> None:
        if enter:
            self.dialogue_text.insert(tk.END, message + "\n")
            self.dialogue_text.see(tk.END)  # 让对话框滚动到最下部以显示最新信息
        else:
            self.dialogue_text.insert(tk.END, message)
    
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
