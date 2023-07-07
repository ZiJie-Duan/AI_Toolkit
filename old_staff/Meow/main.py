from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoard
from setting import SETTING
from audio import AudioRecorderPlayer
from alitts import TextToSpeech
from whisper_api import AudioTranscriber

def main():


    set = SETTING()
    gpt_api = GPT_API(set.GPT_API_KEY)

    memo = Memo(set.memo_file)
    storyboard = StoryBoard(memo,set.back_ground)
        
    tts = TextToSpeech(set.ALI_URL, set.ALI_TOKEN, set.ALI_APPKEY, set.response_file)

    audio_recorder_player = AudioRecorderPlayer(set.audio_file, set.response_file, set.record_duration)
    transcriber = AudioTranscriber(set.GPT_API_KEY)

    while True:
        
        user_input = input("\n\n按下回车键开始录音-------")
        if user_input.lower() == "q":
            break

        print("录制音频")
        audio_recorder_player.record_audio()
        print("音频录制完成，文件名：", set.audio_file)

        transcription = transcriber.get_transcription(set.audio_file)
        print("Transcription result:", transcription)

        #从Storyboard中获取对话历史记录
        messages = storyboard.get_dialogue_history()

        # 添加用户输入到messages
        messages.append({"role": "user", "content": transcription})

        # 使用GPT_API进行查询
        ai_response = gpt_api.query(messages)
        #print(ai_response)

        tts.run(ai_response)

        # 将对话添加到Storyboard并保存到文件中
        storyboard.add_dialogue_entry(user_input, ai_response)
        # 从Storyboard中获取对话历史记录

        print("播放音频")
        audio_recorder_player.play_audio()

if __name__ == "__main__":
    main()

    # while True:
    #     # 向用户询问问题
    #     user_input = input("User: ")

    #     if user_input.lower() == "quit":
    #         break

    #     # 从Storyboard中获取对话历史记录
    #     messages = storyboard.get_dialogue_history()

    #     # 添加用户输入到messages
    #     messages.append({"role": "user", "content": user_input})

    #     # 使用GPT_API进行查询
    #     ai_response = gpt_api.query(messages)

    #     # 将对话添加到Storyboard并保存到文件中
    #     storyboard.add_dialogue_entry(user_input, ai_response)

    #     print(f"Assistant: {ai_response}")
