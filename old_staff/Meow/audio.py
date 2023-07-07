import pyaudio
import wave
import pygame


class AudioRecorderPlayer:
    def __init__(self, input_audio, response_audio, seconds):
        self.input_audio = input_audio
        self.response_audio = response_audio
        self.seconds = seconds

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("开始录音...")

        frames = []

        for i in range(0, int(RATE / CHUNK * self.seconds)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.input_audio, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def play_audio(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.response_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

# def main():
#     audio_filename = 'audio.mp3'
#     record_duration = 5  # 录音时长（秒）

#     audio_recorder_player = AudioRecorderPlayer(audio_filename, record_duration)

#     print("录制音频")
#     audio_recorder_player.record_audio()
#     print("音频录制完成，文件名：", audio_filename)

#     print("播放音频")
#     audio_recorder_player.play_audio()


# if __name__ == '__main__':
#     main()

