from TCP_Client import TCPClient
from StoryBoard import Memo, StoryBoard
from setting import SETTING
from chat_gui import CHAT_GUI
import threading

class CHAT_CORE:

    def __init__(self):
        self.set = SETTING()
        self.tcp_client = TCPClient(server_address=(self.set.host, self.set.port))
        self.memo = Memo(self.set.memo_file)
        self.storyboard = StoryBoard(self.memo, self.set.back_ground)
        self.chat_gui = CHAT_GUI()
        self.dialogue_record = True
    
    def set_chat_gui(self):
        """
        set the callback function of the chat_gui
        """
        self.chat_gui.settings_callback = self.settings
        self.chat_gui.send_message_callback = self.send_message
        self.chat_gui.refresh_dialogue_callback = self.refresh_dialogue
        self.chat_gui.restart_dialogue_callback = self.restart_dialogue
    
    def settings(self,temperature: float, max_tokens: int, scenario: str) -> None:
        """
        set the temperature, max_tokens and scenario
        """
        scenario_chanege = False
        if self.set.scenario != scenario:
            scenario_chanege = True

        if temperature < 0.1 or temperature > 2:
            self.print_info("温度值错误, 请重新设置", "系统")
            return
        
        if max_tokens < 10 or max_tokens > 2000:
            self.print_info("Max_Tokens数错误, 请重新设置", "系统")
            return
        
        self.set.temperature = temperature
        self.set.max_tokens = max_tokens
        self.set.scenario = scenario 
        self.storyboard.back_ground_insert(self.set.back_ground[self.set.scenario])

        self.print_info("设置已保存", "系统")
        if scenario_chanege:
            self.print_info("情景已切换, 正在 '重启对话' ", "系统")
            self.restart_dialogue()
            if scenario == "翻译器":
                self.dialogue_record = False
            else:
                self.dialogue_record = True
        
        # the change of scenario will apply after restart dialogue
    
    def update_dialogue_counter(self) -> None:
        num_of_dialogue = len(self.storyboard.get_dialogue_history())//2
        if num_of_dialogue >= self.set.max_dialogue:
            info = "对话次数已达推荐上限 \n您可以继续进行对话 \n但为了程序稳定 \n推荐您尽快结束对话 \n并点击重启对话按钮"
            self.chat_gui.update_dialogue_counter_text(info, color="red")
        else:
            info = "建议对话次数 剩余：" + str(self.set.max_dialogue - num_of_dialogue)
            self.chat_gui.update_dialogue_counter_text(info)
    
    def restart_dialogue(self) -> None:
        """
        clean the dialogue history and restart the dialogue
        it will also change the back ground of the dialogue
        if the scenario is changed
        """
        self.storyboard.dialogue_history=[]
        self.storyboard.back_ground_insert(self.set.back_ground[self.set.scenario])
        self.storyboard.memo.write_to_file(self.storyboard.dialogue_history)
        self.refresh_dialogue()
        self.print_info("对话已重启", "系统")
        self.print_info("对话开启", "系统")
        self.update_dialogue_counter()
    
    def refresh_dialogue(self) -> None:
        """refresh the dialogue history
         when the dialogue history be mess up or destoryed,
         this function can recover it via the storyboard
        """
        self.chat_gui.clear_dialogue()
        messages = self.storyboard.get_dialogue_history()
        for message in messages:
            if message["role"] == "user":
                self.chat_gui.insert_message("用户: " + message["content"])
            elif message["role"] == "system":
                self.chat_gui.insert_message("[系统]: " + message["content"])
            else:
                self.chat_gui.insert_message("助手: " + message["content"])

    def send_message(self,message: str) -> None:
        """
        send message to the GPT-3 API and get the response
        """
        self.chat_gui.insert_message("用户: " + message)
        task = threading.Thread(target=self.get_server_reply,args=(message,))
        task.start()

    def get_server_reply(self, message: str) -> str:
        messages = self.storyboard.get_dialogue_history()
        messages.append({"role": "user", "content": message})

        data = {"key": self.set.kzf_key,
                "storyboard": messages,
                "temperature": self.set.temperature,
                "max_tokens": self.set.max_tokens}
        
        try:
            ai_response = self.tcp_client.start(data)
        except Exception as e:
            self.print_info("错误信息: " + str(e), "系统错误")
            self.print_info("程序网络模块出现错误,检查网络并请联系开发者", "系统错误")

        if ai_response["info"] == "success":
            reply = ai_response["reply"]
        elif ai_response["info"] == "key_error":
            reply = "程序秘钥错误，请联系开发者，更新程序"

        if self.dialogue_record:   
            self.storyboard.add_dialogue_entry(message,reply)
            self.update_dialogue_counter()
        self.chat_gui.insert_message("助手: " + reply)


    def print_info(self, info: str, type: str) -> None:
        self.chat_gui.insert_message("[{}]: {}".format(type, info))

    def help(self):
        self.print_info("欢迎使用 康中福ChatGPT3.5 代理系统v1.2", "系统")
        self.print_info("请遵循OpenAI使用条例", "系统")
        self.print_info(
        """
保护隐私：请勿在请求中包含您自己、他人或任何个人的敏感信息，如姓名、地址、电话号码、身份证号等。

合法使用：确保您的请求和用途符合您所在国家/地区的法律法规，遵守知识产权、隐私权以及其他相关法律法规。

遵守道德规范: 不要使用API来制作、传播或推广仇恨言论、歧视、暴力、欺凌, 犯罪行为或不道德内容。

使用限制: 遵循OpenAI API使用限制, 不要通过过高频率的请求或自动化程序滥用服务，以避免对系统造成过大负荷。

信息安全: 在分享或公开API的结果时,确保不泄露您的API密钥或包含敏感信息的请求。
        """, "系统")
        self.print_info("此程序将对话记录存储至软件根目录下的memo.json文件", "系统")
        self.print_info("使用方法：", "系统")
        self.print_info("'Temperature', 'Max_Tokens' 修改后需要点击设置进行保存", "系统")
        self.print_info("'情景选择' 修改后将自动 '重启对话' 进行应用", "系统")
        self.print_info("'刷新' 将去除所有的系统提示, 仅保留对话信息", "系统")
        self.print_info("'重启对话' 将清空对话记录, 并重新开始对话", "系统")
        self.print_info("'Temperature' 范围 0.1 - 2.0 ", "系统警告")
        self.print_info("'Max_Tokens' 范围 10 - 2000 ", "系统警告")
        
    
def main():

    try:
        chat_core = CHAT_CORE()
        chat_core.set_chat_gui()
        chat_core.help()
        chat_core.chat_gui.mainloop()
    except Exception as e:
        chat_core.print_info("错误信息: " + str(e), "系统错误")
        chat_core.print_info("程序出现错误, 请联系开发者", "系统错误")
        print(e)
        print("程序出现错误, 请联系开发者")
    return 0
        

if __name__ == "__main__":
    main()
