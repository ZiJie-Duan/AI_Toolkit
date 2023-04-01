import pyaudio
import wave
import pygame


class AudioRecorderPlayer:
    def __init__(self, record_aduiof, play_audiof):
        self.record_aduiof = record_aduiof 
        self.play_audiof = play_audiof 
        self.stop = False #this is the flag to stop the recording

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

        frames = []

        while not self.stop:
            data = stream.read(CHUNK)
            frames.append(data)

        self.stop = False
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.record_aduiof, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def play_audio(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.play_audiof)
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

