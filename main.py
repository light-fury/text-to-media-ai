#main.py

import sys
from database import add_user_content, update_user_content
from image_video_generation import generate_images_and_videos
from notifications import send_notification

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <user_id> <prompt>")
        return

    user_id = sys.argv[1]
    prompt = sys.argv[2]

    # Add DB entry with status "Processing"
    content_id = add_user_content(user_id=user_id, prompt=prompt)

    # Generate images and videos #  5 images and 5 videos are generated
    image_paths, video_paths = generate_images_and_videos(user_id, prompt, n=5, image_size="1024x1024", video_duration=5)

    # Update DB with completed status
    if image_paths or video_paths:
        update_user_content(content_id, image_paths, video_paths, status="Completed")
    else:
        # If no content was generated successfully, still mark completed
        update_user_content(content_id, image_paths=[], video_paths=[], status="Completed")

    # Immediately send notification
    send_notification(user_id, prompt)

if __name__ == "__main__":
    main()
