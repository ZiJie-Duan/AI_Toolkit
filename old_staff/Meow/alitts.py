
import nls

class TextToSpeech:
    def __init__(self, url, token, appkey, file_name):
        self.url = url
        self.token = token
        self.appkey = appkey
        self.file_name = file_name


    def on_metainfo(self, message, *args):
        print("on_metainfo message=>{}".format(message))

    def on_error(self, message, *args):
        print("on_error args=>{}".format(args))

    def on_close(self, *args):
        print("on_close: args=>{}".format(args))

    def on_data(self, data, *args):
        with open(self.file_name, "ab") as f:  # 修改为二进制模式
            f.write(data)

    def on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))

    def run(self,text):
        with open(self.file_name, "wb") as f:  # 修改为二进制模式
            pass
        tts = nls.NlsSpeechSynthesizer(
            url=self.url,
            token=self.token,
            appkey=self.appkey,
            on_metainfo=self.on_metainfo,
            on_data=self.on_data,
            on_completed=self.on_completed,
            on_error=self.on_error,
            on_close=self.on_close
        )

        print("Session start")
        result = tts.start(text, voice="zhimiao_emo", aformat="mp3", sample_rate=16000)
        print("TTS done with result: {}".format(result))


# tts = TextToSpeech(URL, TOKEN, APPKEY)
#tts.run(text)