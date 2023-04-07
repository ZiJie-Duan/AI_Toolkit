from TCP_Client import TCPClient
from StoryBoard import Memo, StoryBoard
from setting import SETTING
from chat_gui import CHAT_GUI

class CHAT_CORE:

    def __init__(self):
        self.set = SETTING()
        self.tcp_client = TCPClient(server_address=(self.set.host, self.set.port))
        self.memo = Memo(self.set.memo_file)
        self.storyboard = StoryBoard(self.memo, self.set.back_ground)
        self.chat_gui = CHAT_GUI()
    
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
        self.set.temperature = temperature
        self.set.max_tokens = max_tokens
        self.set.scenario = scenario 

        self.chat_gui.insert_message("系统: 设置已保存")
        # the change of scenario will apply after restart dialogue
    
    def restart_dialogue(self) -> None:
        """
        clean the dialogue history and restart the dialogue
        it will also change the back ground of the dialogue
        if the scenario is changed
        """
        self.storyboard.dialogue_history=[]
        self.storyboard.back_ground_check(self.set.back_ground)
        self.storyboard.memo.write_to_file(self.storyboard.dialogue_history)
        self.refresh_dialogue()
    
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
                self.chat_gui.insert_message("系统: " + message["content"])
            else:
                self.chat_gui.insert_message("助手: " + message["content"])

    def send_message(self,message: str) -> None:
        """
        send message to the GPT-3 API and get the response
        """
        self.chat_gui.insert_message("用户: " + message)

        messages = self.storyboard.get_dialogue_history()
        messages.append({"role": "user", "content": message})

        data = {"key": self.set.kzf_key,
                "storyboard": messages,
                "temperature": self.set.temperature,
                "max_tokens": self.set.max_tokens}
        ai_response = self.tcp_send(data)
        self.storyboard.add_dialogue_entry(message,ai_response)
        self.chat_gui.insert_message("助手: " + ai_response)

    def tcp_send(self, data_dict: dict) -> str:
        """
        send data to the server and get the response
        """
        reply_dict = self.tcp_client.start(data_dict)
        return reply_dict["reply"]

    
def main():

    chat_core = CHAT_CORE()
    chat_core.set_chat_gui()
    chat_core.chat_gui.mainloop()
    

if __name__ == "__main__":
    main()
