# image_video_generator.py
# Partha Pratim Ray
# 6/12/2024

## runwayml video generation

#################

# First do export runwayml api otherwise it doesnot work, we can't save it the .env file

################# 
######  export RUNWAYML_API_SECRET=YOU-RUNWAYML-API
################
######## For windows, no key export support exists

import os
import time
import requests
import base64
from dotenv import load_dotenv
from runwayml import RunwayML
from openai import OpenAI
from config import OPENAI_API_KEY, RUNWAYML_API_SECRET

load_dotenv()

openai_api_key = OPENAI_API_KEY
runwayml_api_key = RUNWAYML_API_SECRET

if not openai_api_key or not runwayml_api_key:
    raise ValueError("API keys not found. Please add them to .env and config.py.")

openai_client = OpenAI(api_key=openai_api_key)
runwayml_client = RunwayML(api_key=runwayml_api_key)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def generate_single_image(user_id, prompt, size="1024x1024", image_index=1):
    output_folder = os.path.join("generated_content", user_id)
    os.makedirs(output_folder, exist_ok=True)
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            n=1
        )
        image_data = response.data[0]
        image_url = image_data.url
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_path = os.path.join(output_folder, f"image_{image_index}.png")
            with open(image_path, "wb") as file:
                file.write(image_response.content)
            return image_path
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Image generation error: {e}")
        return None

def generate_video(user_id, image_path, prompt, model_name="gen3a_turbo", duration=5, index=1):
    output_folder = os.path.join("generated_content", user_id)
    os.makedirs(output_folder, exist_ok=True)
    try:
        base64_image = encode_image_to_base64(image_path)
        video_task = runwayml_client.image_to_video.create(
            model=model_name,
            prompt_image=f"data:image/png;base64,{base64_image}",
            prompt_text=prompt,
            duration=duration
        )

        task_id = video_task.id
        while True:
            task_status = runwayml_client.tasks.retrieve(id=task_id)
            current_status = task_status.status

            if current_status == "SUCCEEDED":
                if isinstance(task_status.output, list) and len(task_status.output) > 0:
                    video_url = task_status.output[0]
                    video_response = requests.get(video_url)
                    if video_response.status_code == 200:
                        video_path = os.path.join(output_folder, f"video_{index}.mp4")
                        with open(video_path, "wb") as video_file:
                            video_file.write(video_response.content)
                        return video_path
                    else:
                        return None
                else:
                    return None
            elif current_status == "FAILED":
                return None
            else:
                time.sleep(10)
    except Exception as e:
        print(f"[ERROR] Video generation error: {e}")
        return None

def generate_images_and_videos(user_id, prompt, n=5, image_size="1024x1024", video_duration=5):
    image_paths = []
    video_paths = []
    for i in range(1, n+1):
        image_path = generate_single_image(user_id, prompt, size=image_size, image_index=i)
        if image_path:
            image_paths.append(image_path)
            video_path = generate_video(user_id, image_path, prompt=prompt, model_name="gen3a_turbo", duration=video_duration, index=i)
            if video_path:
                video_paths.append(video_path)
    return image_paths, video_paths
