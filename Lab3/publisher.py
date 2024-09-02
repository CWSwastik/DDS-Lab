import requests

def publish_message(topic, message):
    url = 'http://localhost:5000/publish'
    data = {'topic': topic, 'message': message}
    try:
        response = requests.post(url, json=data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if response.status_code == 200:
        print(f"Message published to topic '{topic}'")
    elif response.status_code == 404:
        print(f"Failed to publish message: {response.text}")
    else:
        print(f"An error occurred: {response.status_code}")

if __name__ == "__main__":
    while True:
        # Take topic and message from the user via CLI
        topic = input("Enter topic (or 'exit' to quit): ")
        if topic.lower() == 'exit':
            break
        message = input(f"Enter message to publish to '{topic}': ")

        # Publish the message to the given topic
        publish_message(topic, message)
