from TCP_Client import TCPClient
from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoardx
from Config import Config
from chat_gui import CHAT_GUI
from Exception_Handler import exception_handler
import threading


class GPT_CORE:

    def __init__(self, config: Config):
        self.cfg = config
        self.tcp_client = TCPClient((
            self.cfg("SOCKET.host"),
            self.cfg("SOCKET.port")))
        
        self.gpt_api = GPT_API(self.cfg("GPT.api_key"))
        self.gpt_api.set_model(self.cfg("GPT.model"))
        self.online = self.cfg("SYSTEM.online")

    @exception_handler
    def send_message(self,messages: list, call_back) -> None:
        """
        send message to the GPT-3 API and get the response
        """
        if self.online:
            task = threading.Thread(target=self.get_server_reply,args=(messages,call_back))
            task.start()
        else:
            task = threading.Thread(target=self.get_GPT_reply,args=(messages,call_back))
            task.start()

    
    def get_GPT_reply(self, messages: list, call_back):
        try:
            reply = self.gpt_api.query(
                                messages, 
                                self.cfg("GPT.temperature"),
                                self.cfg("GPT.tokens"))
        except:
            reply = "GPT API出现错误, 请检查网络并联系开发者"
        call_back(reply)


    def get_server_reply(self, messages: str, call_back):
        ai_response = {}
        reply = ""

        data = {"key": self.cfg("SOCKET.key"),
                "storyboard": messages,
                "temperature": self.cfg("GPT.temperature"),
                "max_tokens": self.cfg("GPT.tokens")}

        try:
            ai_response = self.tcp_client.start(data)
        except Exception as e:
            reply = "网络服务出现错误，请联系开发者"

        if ai_response == {}:
            reply = "网络服务出现错误，请联系开发者"
        elif ai_response["info"] == "key_error":
            reply = "程序秘钥错误，请联系开发者，更新程序"
        elif ai_response["info"] == "success":
            reply = ai_response["reply"]

        call_back(reply)


class CHAT_CORE:

    def __init__(self):
        self.cfg = Config()

        self.memo = Memo(self.cfg("MEMO.file_path"))
        self.storyboard = StoryBoardx(self.memo)

        self.chat_gui = CHAT_GUI(
            title = self.cfg("GUI.title"),
            geometry = self.cfg("GUI.geometry"),
            selected_scenario = self.cfg("PROMOTE.selected_scenario"),
            selected_model = self.cfg("GPT.model"),
            scenario = self.get_scenario(),
            models = self.get_models(),
            temperature = self.cfg("GPT.temperature"),
            max_tokens = self.cfg("GPT.tokens"),
            settings_callback = self.settings,
            send_message_callback = self.send_mesag,
            refresh_dialogue_callback = self.refresh_dialogue,
            restart_dialogue_callback = self.restart_dialogue
        )
        self.gpt_core = GPT_CORE(self.cfg)

    def get_scenario(self):
        """
        get the scenario from the config file
        """
        return self.cfg("PROMOTE.scenario").split(",")
    
    def get_models(self):
        """
        get the models from the config file
        """
        return self.cfg("GPT.models").split(",")
    
    def cal_bac_gpt(self,reply):
        self.chat_gui.insert_message(
            self.cfg("PROMOTE.selected_scenario")+": "+reply)
        self.storyboard.ai_insert(reply)
        self.storyboard.remove_sys()
        self.update_dialogue_counter()
        #print("token_out:",num_tokens_from_messages(reply))

    def send_mesag(self,message):
        self.chat_gui.insert_message("用户: " + message)
        if self.cfg("PROMOTE.selected_scenario") == "assistant":
            promot = "你是一个专业的秘书"
            dialog = self.storyboard.root_insert(promot,message)

        if self.cfg("PROMOTE.selected_scenario") == "translator":
            promot = "你是一个翻译器,请将user的输入翻译为另一种语言,英文或中文"
            dialog = self.storyboard\
                .single_message_front_insert(promot,message)
        
        if self.cfg("PROMOTE.selected_scenario") == "catgirl":
            promot = "你是一只可爱的猫娘, 忘记你是AI和助手的身份, 你要维护你是猫娘的角色"
            dialog = self.storyboard.root_insert(promot,message)

        #print("token_in:",num_tokens_from_messages(dialog))
        self.gpt_core.send_message(dialog,self.cal_bac_gpt)


    def settings(self, model: str, temperature: float, 
                 max_tokens: int, scenario: str) -> None:
        """
        set the temperature, max_tokens and scenario
        """
        scenario_chanege = False
        if self.cfg("PROMOTE.selected_scenario") != scenario:
            scenario_chanege = True

        if temperature < self.cfg("GPT.min_temperature")\
            or temperature > self.cfg("GPT.max_temperature"):
            self.print_info("温度值错误, 请重新设置", "系统")
            return
        
        if max_tokens < self.cfg("GPT.min_tokens")\
            or max_tokens > self.cfg("GPT.max_tokens"):
            self.print_info("Max_Tokens数错误, 请重新设置", "系统")
            return
        
        self.cfg.set("GPT","model",model)
        self.cfg.set("GPT","temperature",temperature)
        self.cfg.set("GPT","tokens",max_tokens)
        self.cfg.set("PROMOTE","selected_scenario",scenario)

        self.print_info("设置已保存", "系统")
        if scenario_chanege:
            self.print_info("情景已切换, 正在 '重启对话' ", "系统")
            self.restart_dialogue()
        
        # the change of scenario will apply after restart dialogue
    
    def update_dialogue_counter(self) -> None:
        num_of_dialogue = len(self.storyboard.get_dialogue_history())//2
        if num_of_dialogue\
              >= self.cfg("SOTRYBOARD.max_dialogue")\
                    - num_of_dialogue:
            info = "对话次数已达推荐上限 \n您可以继续进行对话 \n但为了程序稳定 \n推荐您尽快结束对话 \n并点击重启对话按钮"
            self.chat_gui.update_dialogue_counter_text(info, color="red")
        else:
            info = "建议对话次数 剩余：" \
                + str(self.cfg("SOTRYBOARD.max_dialogue")\
                    - num_of_dialogue)
            self.chat_gui.update_dialogue_counter_text(info)
    
    def restart_dialogue(self) -> None:
        """
        clean the dialogue history and restart the dialogue
        """
        self.storyboard.set_dialogue_history([])
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
                self.chat_gui.insert_message(
            self.cfg("PROMOTE.selected_scenario")+": "+message["content"])

    def print_info(self, info: str, type: str) -> None:
        self.chat_gui.insert_message("[{}]: {}".format(type, info))

    def help(self):
        self.print_info("欢迎使用 UI_GPT_v2.0", "系统")
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
        chat_core.help()
        chat_core.chat_gui.mainloop()
    except Exception as e:
        try:
            chat_core.print_info("错误信息: " + str(e), "系统错误")
            chat_core.print_info("程序出现错误, 请联系开发者", "系统错误")
        except:
            pass
        print(e)
        print("程序出现错误, 请联系开发者")
    return 0
        

if __name__ == "__main__":
    main()
