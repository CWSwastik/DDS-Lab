import socketio

# Create a SocketIO client
sio = socketio.Client()

# Connect to the server
sio.connect('http://localhost:5000')

# Callback generator for handling different topics
def get_topic_handler(topic):
    def handle_message(data):
        print(f"Received message for topic '{topic}': {data}")
    
    return handle_message

def subscribe_to_topic(topic):
    sio.emit('subscribe', {'topic': topic})
    sio.on(topic, get_topic_handler(topic))
    print(f"Subscribed to topic '{topic}'")

def unsubscribe_from_topic(topic):
    sio.emit('unsubscribe', {'topic': topic})
    print(f"Unsubscribed from topic '{topic}'")

if __name__ == "__main__":
    while True:
        ch = input("Enter 1 to subscribe\n2 to unsubscribe\n3 to start listening for messages\n4 to exit: ")
        if ch == "1":
            topic = input("Enter topic to subscribe: ")
            subscribe_to_topic(topic)
        elif ch == "2":
            topic = input("Enter topic to unsubscribe: ")
            unsubscribe_from_topic(topic)
        elif ch == "3":
            sio.wait() # Keep the connection open to receive messages
        else:
            break
