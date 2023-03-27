from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoard
from setting import SETTING

if __name__ == "__main__":
    set = SETTING()
    API_KEY = set.api_key
    gpt_api = GPT_API(API_KEY)

    memo = Memo(set.memo_file)
    storyboard = StoryBoard(memo,set.back_ground)

    while True:
        # 向用户询问问题
        user_input = input("User: ")

        if user_input.lower() == "quit":
            break

        # 从Storyboard中获取对话历史记录
        messages = storyboard.get_dialogue_history()

        # 添加用户输入到messages
        messages.append({"role": "user", "content": user_input})

        # 使用GPT_API进行查询
        ai_response = gpt_api.query(messages)

        # 将对话添加到Storyboard并保存到文件中
        storyboard.add_dialogue_entry(user_input, ai_response)

        print(f"Assistant: {ai_response}")
