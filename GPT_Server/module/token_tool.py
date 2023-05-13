import tiktoken

class TokenCounter:

    def __init__(self) -> None:
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def get_token(self,model,messages,process="Completion"): 
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant

        if model == "gpt-3.5-turbo":
            return int(num_tokens)
        
        if model == "gpt-4":
            if process == "Completion":
                return int(num_tokens * 30)
            elif process == "Prompt":
                return int(num_tokens * 15)
            
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
                