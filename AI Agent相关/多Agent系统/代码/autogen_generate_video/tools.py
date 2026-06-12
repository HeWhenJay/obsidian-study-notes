import os
import textwrap
import tempfile
import shutil
import subprocess
import requests
import urllib.parse
import base64
import uuid
import platform
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("API_BASE_URL"),
)

def generate_voiceovers(messages: list[str]) -> list[str]:
    """
    使用豆包TTS API为消息列表生成语音
    参数:
        messages: 需要转换为语音的消息列表
    返回:
        生成的音频文件路径列表
    """

    # 获取环境变量
    appid = os.getenv("DOUBAO_APPID")
    access_token = os.getenv("DOUBAO_ACCESS_TOKEN")
    
    # 创建保存目录
    os.makedirs("voiceovers", exist_ok=True)

    # 检查是否包含了takeaway（如果messages长度比captions多1个）
    # 如果是，则只处理captions部分（跳过第一个消息）
    if len(messages) > 5 and messages[0] != messages[1]:  # 假设captions长度为5
        print("检测到包含takeaway的消息列表，将只处理captions部分")
        messages = messages[1:]  # 跳过第一个消息（takeaway）
    
    # 检查已存在的文件
    audio_file_paths = []
    for i in range(1, len(messages) + 1):
        file_path = f"voiceovers/voiceover_{i}.mp3"
        if os.path.exists(file_path):
            audio_file_paths.append(file_path)
            
    # 如果所有文件已存在则直接返回
    if len(audio_file_paths) == len(messages):
        print("所有语音文件已存在，跳过生成过程。")
        return audio_file_paths
        
    # 逐个生成缺失的文件
    audio_file_paths = [] # 重新初始化以确保只包含实际生成或确认存在的文件
    for i, message in enumerate(messages, 1):
        try:
            save_file_path = f"voiceovers/voiceover_{i}.mp3"
            if os.path.exists(save_file_path):
                print(f"文件 {save_file_path} 已经存在，跳过生成。")
                audio_file_paths.append(save_file_path)
                continue

            print(f"生成语音 {i}/{len(messages)}...")
            
            request_json = {
                "app": {
                    "appid": appid,
                    "token": access_token,
                    "cluster": "volcano_tts"
                },
                "user": {
                    "uid": "388808087185088"
                },
                "audio": {
                    "voice_type": "BV700_V2_streaming",
                    "encoding": "mp3",
                    "speed_ratio": 1.0,
                    "volume_ratio": 1.0,
                    "pitch_ratio": 1.0,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": message,
                    "text_type": "plain",
                    "operation": "query",
                    "with_frontend": 1,
                    "frontend_type": "unitTson"
                }
            }

            header = {"Authorization": f"Bearer;{access_token}"}
            resp = requests.post("https://openspeech.bytedance.com/api/v1/tts", json=request_json, headers=header)
            resp_data = resp.json()

            if "data" in resp_data:
                audio_data = base64.b64decode(resp_data["data"])
                with open(save_file_path, "wb") as f:
                    f.write(audio_data)
                print(f"语音 {i} 生成成功")
                audio_file_paths.append(save_file_path)
            else:
                print(f"Error generating voice {i}: {resp_data.get('message', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error generating voiceover for message: {message}. Error: {e}")
            continue
            
    return audio_file_paths


def generate_images(prompts: list[str],translate: bool = True):
    """
    使用 Pollinations.AI API根据文本提示生成图像
    （Pollinations.AI 是一家总部位于柏林的开源 AI 初创公司，
    提供最易用的免费文本和图像生成 API，无需注册或 API 密钥。国内可用；免费开源；支持web和API接口调用）
    参数:
        prompts: 用于生成图像的文本提示列表
        translate: 是否将中文提示翻译为英文，默认为True
    """
    seed = 42
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)
    

    params = {
        "width": 1536,
        "height": 1536,
        "seed": seed,
        "model": "flux",
        "nologo": "true"
    }
    
    for i, prompt in enumerate(prompts, 1):
        base_url = f"https://gen.pollinations.ai/image/"
        if translate:
            try:
                print(f"正在翻译提示: {prompt}")
                response = client.chat.completions.create(
                    model="qwen-max", 
                    messages=[
                        {"role": "system", "content": "你是一个翻译助手。请将中文提示翻译成英文，以便用于图像生成。保留原始意思但优化为适合图像生成的措辞。只返回翻译后的英文文本，不要包含任何解释或额外内容。"},
                        {"role": "user", "content": f"请将以下中文提示翻译成英文：\n{prompt}"}
                    ],
                    temperature=0.3,
                )
                translated_prompt = response.choices[0].message.content.strip()
                print(f"翻译结果: {translated_prompt}")
                prompt = translated_prompt
            except Exception as e:
                print(f"翻译失败: {e}，将使用原始提示")

        print(f"生成图片 {i}/{len(prompts)} for prompt: {prompt}")
        image_path = os.path.join(output_dir, f"image_{i}.jpg")
        if not os.path.exists(image_path):
            try:
                encoded_prompt = urllib.parse.quote(prompt)
                print('encoded_prompt:',encoded_prompt)
                url = f"{base_url}{encoded_prompt}"
                print('url:',url)
                pollinations_api_key = os.getenv("POLLINATIONS_API_KEY")
                headers = {"Authorization": f"Bearer {pollinations_api_key}"} if pollinations_api_key else {}
                response = requests.get(url, params=params,headers=headers, timeout=300)
                
                if response.status_code == 200:
                    with open(image_path, "wb") as image_file:
                        image_file.write(response.content)
                    print(f"图像已保存至 {image_path}")
                else:
                    print(f"生成图像 {i} 时出错: HTTP状态码 {response.status_code}")
                    if response.text:
                        print(f"错误详情: {response.text}")
            except Exception as e:
                print(f"生成图像 {i} 时出错: {e}")
        else:
            print(f"图像 {image_path} 已存在，跳过生成。")


def sanitize_text_for_ffmpeg(text: str) -> str:
    """
    辅助函数：处理文本使其适用于FFmpeg的drawtext滤镜 (如果直接嵌入文本而不是用textfile)
    对于textfile方式，主要问题是文件内容本身，而不是ffmpeg命令中的文本。
    这个函数目前在代码中未使用，因为字幕是通过textfile加载的。
    如果未来改为直接在命令行中设置text，则此函数很重要。
    """
    text = text.replace('\\', '\\\\') # 转义反斜杠
    text = text.replace("'", "\\'")  # 转义单引号
    text = text.replace(':', '\\:')  # 转义冒号
    text = text.replace(',', '\\,')  # 转义逗号
    text = text.replace(';', '\\;')  # 转义分号
    return text

def escape_ffmpeg_path_for_filter(path_str: str) -> str:
    """
    辅助函数：为FFmpeg滤镜参数中的路径字符串进行转义。
    - 将反斜杠替换为正斜杠。
    - 转义Windows驱动器盘符后的冒号 (例如 C:/path -> C\\:/path Python字符串, FFmpeg看到 C\:/path)。
    """
    path = path_str.replace('\\', '/')
    # 检查是否为Windows驱动器路径，如 "C:/..."
    if len(path) >= 2 and path[1] == ':' and path[0].isalpha():
        # 转义冒号: "C:/" 变为 "C\\:/" (Python字符串层面)
        # 这将使 "C\:" 传递给FFmpeg的滤镜解析器
        path = path[0] + '\\:' + path[2:]
    return path

def wrap_caption(caption: str, max_width=20) -> str:
    """
    辅助函数：将字幕文本换行处理以提高可读性
    Args:
        caption: 需要换行的文本
        max_width: 每行最大字符数
    Returns:
        包含换行符的格式化字符串
    """
    wrapped_lines = textwrap.wrap(caption, width=max_width)
    return "\n".join(wrapped_lines)


def generate_video(captions: list[str]):
    """
    用ffmpeg生成YouTube Shorts风格视频，包含动态图片、语音和背景音乐
    Args:
        captions: 每个视频片段要显示的字幕列表
    """
    # 配置参数
    images_folder = "images"
    voiceovers_folder = "voiceovers"
    music_file = "music/背景音乐.mp3" # 背景音乐文件（需自行添加）
    output_video = "yt_shorts_video2.mp4"
    IMAGE_DURATION = 5 # 每个图片片段的持续时间（秒）
    
    # 获取排序后的图片和配音文件列表
    images = sorted([
        os.path.join(images_folder, f) 
        for f in os.listdir(images_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ])
    
    voiceovers = sorted([
        os.path.join(voiceovers_folder, f)
        for f in os.listdir(voiceovers_folder)
        if f.lower().endswith(".mp3")
    ])

    # 输入验证
    if len(images) != len(voiceovers):
        raise ValueError("图片数量与语音文件数量不匹配！")
    
    if captions is None:
        captions = [os.path.splitext(os.path.basename(vo))[0] for vo in voiceovers]
        print('captions:',captions)
    elif len(captions) != len(images):
        raise ValueError("字幕数量与图片数量不匹配！")

    total_duration = len(images) * IMAGE_DURATION
    print(f"总时长: {total_duration} 秒")

    temp_dir = tempfile.mkdtemp(prefix="video_gen_")
    print(f"使用临时目录: {temp_dir}")

    try:
        segment_files = []
        # 步骤1：创建单个视频片段（含动态效果和字幕）
        for i, (image_path_original, caption) in enumerate(zip(images, captions)):
            # --- 修改点 ---
            # 规范化输入图片路径给ffmpeg -i (通常相对路径或正斜杠绝对路径较好)
            current_image_path_for_ffmpeg_input = image_path_original.replace("\\", "/")

            # 字幕处理 (与之前相同)
            # safe_caption = sanitize_text_for_ffmpeg(caption) # 如果直接用text=...才需要
            wrapped_caption = wrap_caption(caption) # caption已经是原始文本，无需 sanitize
            
            # 字幕文件路径 (写入时用原始路径，滤镜中用转义后路径)
            raw_caption_file_os_path = os.path.join(temp_dir, f"caption_{i}.txt")
            caption_file_for_ffmpeg_filter = escape_ffmpeg_path_for_filter(raw_caption_file_os_path)
            
            # 片段输出路径 (规范化)
            segment_output_path = os.path.join(temp_dir, f"segment_{i}.mp4").replace("\\", "/")
            

            with open(raw_caption_file_os_path, "w", encoding="utf-8") as f:
                f.write(wrapped_caption)
            
            # 字体路径
            if platform.system() == "Windows":
                font_path_for_ffmpeg_filter = "C\\:/Windows/Fonts/simhei.ttf"
            elif platform.system() == "Darwin": # macOS
                font_path_for_ffmpeg_filter = "/Library/Fonts/SimHei.ttf"
            else: # Linux 等
                # 尝试一个常见的 Linux 中文字体路径
                font_path_for_ffmpeg_filter = "/usr/share/fonts/truetype/wqy/wqy-zenhei/wqy-zenhei.ttc"
                if not os.path.exists(font_path_for_ffmpeg_filter):
                    font_path_for_ffmpeg_filter = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" # 另一个例子
                    if not os.path.exists(font_path_for_ffmpeg_filter):
                        print("警告：未找到指定的中文字体，请手动配置字体路径！")
                        font_path_for_ffmpeg_filter = "sans-serif"
            # --- 修改点结束 ---
            
            # 视频滤镜组合（动态效果+字幕）
            video_filter = (
                # 动态缩放效果（Ken Burns效果）
                "scale=-1:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920:x=(in_w-1080)*(t/{IMAGE_DURATION}):y=0,"
                f"drawtext=textfile='{caption_file_for_ffmpeg_filter}':" # 使用转义后的字幕文件路径
                f"fontfile='{font_path_for_ffmpeg_filter}':"
                "fontsize=64:fontcolor=white:"                           # 字体大小和颜色
                "box=1:boxcolor=black@0.6:boxborderw=10:"                # 背景框设置
                "line_spacing=10:"                                       # 行间距
                "x=(w-text_w)/2:"                                       # 水平居中
                "y=h-text_h-150:"                                       # 底部上方150像素
                "alpha=1"                                               # 透明度
            )
            
            # FFmpeg生成片段命令
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",               # 循环输入图片
                "-i", current_image_path_for_ffmpeg_input, # 使用规范化的图片路径
                "-vf", video_filter,        # 应用视频滤镜
                "-t", str(IMAGE_DURATION),   # 设置片段时长
                "-c:v", "h264",             # 视频编码器
                "-preset", "medium",        # 编码预设
                "-crf", "23",                # 质量参数
                "-pix_fmt", "yuv420p",       # 像素格式
                segment_output_path # 使用规范化的片段输出路径
            ]
            
            print(f"\n正在生成片段 {i+1}/{len(images)}...")
            print(f"FFmpeg command for segment: {' '.join(cmd)}") # 打印命令用于调试
            subprocess.run(cmd, check=True, capture_output=True, text=True) 
            segment_files.append(segment_output_path)

        # 步骤2：拼接所有视频片段
        print("\n合并视频片段...")
        concat_list_path = os.path.join(temp_dir, "concat_list.txt").replace("\\","/")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for segment in segment_files:
                # segment已经是正斜杠路径，且concat demuxer对路径中的:通常不敏感 (C:/path)
                # 但为保险，如果需要，也可以对segment路径做更严格的转义或确保不含特殊字符
                f.write(f"file '{segment}'\n") # 单引号包围路径

        silent_video_path = os.path.join(temp_dir, "silent_video.mp4").replace("\\","/")
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",         # 使用拼接协议
            "-safe", "0",           # 允许任意文件路径
            "-i", concat_list_path,
            "-c", "copy",           # 直接流复制
            silent_video_path
        ]
        print(f"FFmpeg command for concat: {' '.join(concat_cmd)}")
        subprocess.run(concat_cmd, check=True, capture_output=True, text=True)

        # 步骤3：混合音频（语音+背景音乐）
        print("\n混合音频...")
        final_audio_path = os.path.join(temp_dir, "final_audio.mp3").replace("\\","/")
        
        # 构建复杂音频滤镜
        filter_parts = []
        delayed_refs = []
        
        # 处理每个语音文件
        for i_vo, voiceover_path_original in enumerate(voiceovers):
            voiceover_path_input = voiceover_path_original.replace("\\","/")
            # 计算延迟时间
            start_ms = i_vo * IMAGE_DURATION * 1000
            filter_parts.append(
                f"[{i_vo}:a]asetpts=PTS-STARTPTS,"                            # 重置时间戳
                f"volume=2.5,adelay={start_ms}|{start_ms}[vo_delayed{i_vo}];" # 调整音量和延迟
            )
            delayed_refs.append(f"[vo_delayed{i_vo}]")

        # 混合所有语音
        filter_parts.append(
            "".join(delayed_refs) +
            f"amix=inputs={len(voiceovers)}:duration=longest:normalize=0[voicemix];"
            "[voicemix]volume=2.5[voicemix_loud];" # 提升整体音量
        )
        
        # 处理背景音乐
        music_index = len(voiceovers)
        music_file_input = music_file.replace("\\","/")
        filter_parts.append(
            f"[{music_index}:a]"
            "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo," # 统一音频格式
            "volume=0.8," # 降低音乐音量
            f"afade=t=out:st={total_duration-1}:d=1[musicvol];" # 添加淡出效果
            f"[musicvol]atrim=0:{total_duration},asetpts=PTS-STARTPTS[music];" # 修剪时长
        )

        # 混合语音和背景音乐
        filter_parts.append(
            f"[voicemix_loud]apad=whole_dur={total_duration}[voicepadded];" # 填充静音
            "[voicepadded][music]amix=inputs=2:duration=first:normalize=0[afinal]"  # 最终混合
        )
        
        # 构建并执行音频混合命令
        audio_filter_complex = "".join(filter_parts)
        audio_cmd = ["ffmpeg", "-y"]
        
        # 添加所有语音文件作为输入
        for vo_path_original in voiceovers:
            audio_cmd.extend(["-i", vo_path_original.replace("\\","/")])
        
        # 添加背景音乐文件作为输入
        audio_cmd.extend(["-i", music_file_input])
        
        # 补全命令参数
        audio_cmd.extend([
            "-filter_complex", audio_filter_complex,
            "-map", "[afinal]",
            "-c:a", "mp3", 
            final_audio_path
        ])
        print(f"FFmpeg command for audio mix: {' '.join(audio_cmd)}")
        subprocess.run(audio_cmd, check=True, capture_output=True, text=True)

        # 步骤4：合成最终视频
        print("\n合成最终视频...")
        final_cmd = [
            "ffmpeg", "-y",
            "-i", silent_video_path, 
            "-i", final_audio_path,  
            "-c:v", "copy", # 直接复制视频流
            "-c:a", "aac", # 重新编码音频
            "-shortest", # 以最短输入为准
            output_video 
        ]
        print(f"FFmpeg command for final merge: {' '.join(final_cmd)}")
        subprocess.run(final_cmd, check=True, capture_output=True, text=True)

        print(f"\n视频生成成功: {output_video}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed with exit code {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e_gen:
        print(f"An error occurred during video generation: {e_gen}")
    finally:
        print(f"正在清理临时文件...")
        shutil.rmtree(temp_dir, ignore_errors=True)
