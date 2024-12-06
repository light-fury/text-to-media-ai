#notifications.py

def send_notification(user_id, prompt):
    # Terminal notification
    print(f"Notification: Content for user {user_id} with prompt '{prompt}' is now ready!")
    print(f"Visit http://localhost:5000/?user_id={user_id} to view your content.")
