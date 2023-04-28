from GPT_API import GPT_API
from StoryBoard import Memo, StoryBoard
from setting import SETTING
from whisper_api import AudioTranscriber
import os
from pydub import AudioSegment


def write_text_to_file(path: str, text: str) -> None:
    """
    将一个巨大的字符串（text）写入到指定路径的文件中，默认文件类型为txt。

    :param path: 文件路径，str类型
    :param text: 要写入文件的字符串，str类型
    """
    
    # 将文本写入文件
    with open(path, "a", encoding="utf-8") as file:
        file.write(text)



def change_filename(path, new_name):
    # 分离路径和扩展名
    file_dir, file_ext = os.path.splitext(path)
    
    # 分离目录和文件名
    dir_path, _ = os.path.split(file_dir)
    
    # 构建新的文件路径
    new_file_path = os.path.join(dir_path, new_name + file_ext)
    
    return new_file_path


def split_audio(input_file_path, split_duration):
    # 加载音频文件
    audio = AudioSegment.from_mp3(input_file_path)
    
    # 计算分割段数（包括最后一段不完整的音频）
    split_count = int(len(audio) / (split_duration * 1000)) + 1
    
    # 初始化结果列表
    split_files = []

    # 遍历分割段数，逐段分割音频
    for i in range(split_count):
        start_time = i * split_duration * 1000
        end_time = (i + 1) * split_duration * 1000

        # 分割音频
        split_audio = audio[start_time:end_time]

        # 保存分割后的音频文件
        output_file_path = change_filename(input_file_path, f"split_{i}_{os.path.basename(input_file_path)}")
        split_audio.export(output_file_path, format="mp3")

        # 将音频文件路径添加到结果列表中
        split_files.append(output_file_path)
        print("分割完成：", output_file_path)
        print("进度：{}/{}".format(i, split_count - 1))

    return split_files


# 示例
# input_file_path = r"C:\Peter_program_test\audio.mp3"
# split_duration = 300  # 单位：秒

# split_files = split_audio(input_file_path, split_duration)
# print("分割后的音频文件路径：")
# for file in split_files:
#     print(file)

# input("FINISH")

def main():

    set = SETTING()
    #gpt_api = GPT_API(set.GPT_API_KEY)

    memo = Memo(set.memo_file)
    storyboard = StoryBoard(memo,set.back_ground)
    transcriber = AudioTranscriber(set.GPT_API_KEY)

    audio_files = split_audio(r"C:\Peter_program_test\audio.mp3",120)
    #audio_files = ['C:\\Peter_program_test\\split_0_audio.mp3.mp3', 'C:\\Peter_program_test\\split_1_audio.mp3.mp3', 'C:\\Peter_program_test\\split_2_audio.mp3.mp3', 'C:\\Peter_program_test\\split_3_audio.mp3.mp3', 'C:\\Peter_program_test\\split_4_audio.mp3.mp3', 'C:\\Peter_program_test\\split_5_audio.mp3.mp3', 'C:\\Peter_program_test\\split_6_audio.mp3.mp3', 'C:\\Peter_program_test\\split_7_audio.mp3.mp3', 'C:\\Peter_program_test\\split_8_audio.mp3.mp3', 'C:\\Peter_program_test\\split_9_audio.mp3.mp3', 'C:\\Peter_program_test\\split_10_audio.mp3.mp3', 'C:\\Peter_program_test\\split_11_audio.mp3.mp3', 'C:\\Peter_program_test\\split_12_audio.mp3.mp3', 'C:\\Peter_program_test\\split_13_audio.mp3.mp3', 'C:\\Peter_program_test\\split_14_audio.mp3.mp3', 'C:\\Peter_program_test\\split_15_audio.mp3.mp3', 'C:\\Peter_program_test\\split_16_audio.mp3.mp3', 'C:\\Peter_program_test\\split_17_audio.mp3.mp3', 'C:\\Peter_program_test\\split_18_audio.mp3.mp3', 'C:\\Peter_program_test\\split_19_audio.mp3.mp3', 'C:\\Peter_program_test\\split_20_audio.mp3.mp3', 'C:\\Peter_program_test\\split_21_audio.mp3.mp3', 'C:\\Peter_program_test\\split_22_audio.mp3.mp3', 'C:\\Peter_program_test\\split_23_audio.mp3.mp3', 'C:\\Peter_program_test\\split_24_audio.mp3.mp3', 'C:\\Peter_program_test\\split_25_audio.mp3.mp3', 'C:\\Peter_program_test\\split_26_audio.mp3.mp3']
    drop_to = 0
    
    for i in range(len(audio_files)):

        if i < drop_to:
            continue
        print("开始转换",i)
        transcription = transcriber.get_transcription(audio_files[i])
        write_text_to_file("subtitles.txt",transcription)
        print("Transcription result: {}".format(transcription))
        print("({}/{}) ".format(i,len(audio_files)-1))


    print("FINISH")


        # #从Storyboard中获取对话历史记录
        # messages = storyboard.get_dialogue_history()

        # # 添加用户输入到messages
        # messages.append({"role": "user", "content": transcription})

        # # 使用GPT_API进行查询
        # ai_response = gpt_api.query(messages)
        # #print(ai_response)


        # # 将对话添加到Storyboard并保存到文件中
        # storyboard.add_dialogue_entry(user_input, ai_response)
        # # 从Storyboard中获取对话历史记录

        # print("播放音频")
        # audio_recorder_player.play_audio()

if __name__ == "__main__":
    main()

