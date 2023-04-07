from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoard
from setting import SETTING
from audio import AudioRecorderPlayer
from whisper_api import AudioTranscriber
import threading


def main():
    """
    a translator that can translate your voice to text
    then translate english to chinese or chinese to english
    """

    print("\nPeter's translator V1.0\n")
    print("\npress q to quit...\n")
    
    set = SETTING()
    gpt_api = GPT_API(set.GPT_API_KEY)

    memo = Memo(set.memo_file)
    storyboard = StoryBoard(memo,set.back_ground)

    audio_recorder_player = AudioRecorderPlayer(set.record_aduiofile, set.play_audiofile)
    transcriber = AudioTranscriber(set.GPT_API_KEY)

    while True:
        
        user_input = input("\npress enter to record audio:")
        if user_input.lower() == "q":
            break

        print("strat recording audio...")
        thread1 = threading.Thread(target=audio_recorder_player.record_audio)
        thread1.start()

        user_input = input("press enter to stop recording audio:")
        audio_recorder_player.stop = True
        print("...stop recording audio")

        thread1.join()

        record_transcription = transcriber.get_transcription(set.record_aduiofile)
        print("\n\nUntranslated Sentence:", record_transcription)

        #从Storyboard中获取对话历史记录
        messages = storyboard.get_dialogue_history()

        # 添加用户输入到messages
        messages.append({"role": "user", "content": record_transcription})

        # 使用GPT_API进行查询
        ai_response = gpt_api.query(messages,max_tokens=200)
        #print(ai_response)

        print("Translated Result:", ai_response)

if __name__ == "__main__":
    main()
