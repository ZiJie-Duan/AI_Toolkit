
class PromoteBase:

    def __init__(self,StoryBoard,config):
        self.StoryBoard = StoryBoard
        self.config = config

    def clean_dialogue(self):
        dialog = self.StoryBoard.get_dialogue_history()
        dialog = [log for log in dialog if log["role"] != "system"]
        self.StoryBoard.set_dialogue_history(dialog)

    def promote(self, input: str):
        pass

    def distinguish(self, input: str):
        pass


class Promote(PromoteBase):

    def __init__(self,StoryBoard,config):
        super().__init__(StoryBoard,config)

    def promote(self, input: str):

        scenario = self.config.get("PROMOTE","selected_scenario")
        if scenario == "assitant":
            return self.assistant(input)
        elif scenario == "translator":
            return self.translator(input)
        elif scenario == "catgirl":
            return self.catgirl(input)
    
    def assistant(self, input: str):
        promote = """
        你是一个专业的秘书
        """ 
        dialog = self.StoryBoard.get_dialogue_history()
        dialog.insert(0, promote)
        dialog.append({"role":"user","content":input})
        return dialog
        
    def assistant_back(self, input: list, reply: str):
        reply = {"role":self.config.get("PROMOTE","selected_scenario")\
                       ,"content":reply}
        self.StoryBoard.add_dialogue_entry(input[-1],reply)


    def translator(self, input: str):
        pass

    def translator_call_back(self, input: list, reply: str, update):
        pass

    def catgirl(self, input: str):
        pass

    def catgirl_call_back(self, input: list, reply: str, update):
        pass

    


    


    


    

