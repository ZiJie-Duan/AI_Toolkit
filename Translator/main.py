from module.Config import Config
from module.GPT_API import GPT_API
from module.StoryBoard import StoryBoard, Memo
from audio import AudioRecorderPlayer
from whisper_api import AudioTranscriber
import threading

LOCK = 0

class TranslatorStoryBoard(StoryBoard):

    def __init__(self, memo: Memo = None):
        super().__init__(memo)

    def get_message(self, prompt: str, text = None) -> list:
        self.add_dialogue("system", prompt)
        self.add_dialogue("user", text)
        result = self.get_dialogue_history()
        self.set_dialogue_history([])
        return result


def translate(audio_recorder_player,transcriber,storyboard,gpt_api,cfg):
    
    global LOCK
    LOCK = 1

    print("[Start Recording]...")
    thread1 = threading.Thread(target=audio_recorder_player.record_audio)
    thread1.start()

    input("[Waiting for Stop]...]")
    audio_recorder_player.stop = True
    print("[Stop Recording]...")
    LOCK = 0

    thread1.join()

    record_transcription = transcriber.get_transcription(cfg("SYS.record_aduiofile"))
    print("\n------------[Original Text]:", record_transcription)

    prompt = "翻译user发送的文本至中文"
    messages = storyboard.get_message(prompt, record_transcription)
    # 使用GPT_API进行查询
    ai_response = gpt_api.query(messages,max_tokens=200)
    #print(ai_response)

    print("\n------------[Translated Text]:", ai_response)


def main():
    """
    a translator that can translate your voice to text
    then translate english to chinese or chinese to english
    """

    cfg = Config()

    print("\nPeter's translator V1.1\n")
    print("\npress q to quit...\n")
    
    gpt_api = GPT_API(cfg("GPT.key"))
    memo = Memo(cfg("SYS.memo"))
    storyboard = TranslatorStoryBoard(memo)

    audio_recorder_player = AudioRecorderPlayer(cfg("SYS.record_aduiofile"), cfg("SYS.play_audiofile"))
    transcriber = AudioTranscriber(cfg("GPT.key"))

    while True:

        if LOCK == 1:
            continue

        user_input = input("[Waiting for Start]:")
        if user_input.lower() == "q":
            break

        tt = threading.Thread(target=translate,
                args=(audio_recorder_player,transcriber,storyboard,gpt_api,cfg))
        tt.start()

if __name__ == "__main__":
    main()
