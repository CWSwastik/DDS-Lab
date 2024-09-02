# **Labsheet 3: Implementing Pub/Sub Model Using Python and Socket.IO**

**Objective**: By the end of this lab, you will be able to design and implement a Pub/Sub (Publisher-Subscriber) model using Python and Socket.IO. You will understand how to manage topics, subscribe clients, and publish messages in a real-time system.

---

## **Overview**

In this lab, you will create a Pub/Sub system using Socket.IO:

- **Publisher**: Sends messages to specific channels.
- **Subscriber**: Subscribes to channels to receive messages.
- **Server**: Manages the topics, channels, subscriptions, and message distribution.

![image](https://github.com/user-attachments/assets/4530e1e3-8663-4e02-871a-66c99c7fa5d9)


---

## **Part 1: Understanding Pub/Sub and Socket.IO Rooms**

### **Explanation**:

The **Publish-Subscribe (Pub/Sub)** model is a messaging pattern where:

- **Publisher**: A component that sends messages to a certain topic or channel.
- **Subscriber**: A component that subscribes to a topic or channel to receive messages.
- **Broker**: The intermediary that manages the topics, subscriptions, and distributes messages from publishers to subscribers.

In a Pub/Sub system, publishers and subscribers are decoupled. The publisher doesn't know who the subscribers are, and subscribers don't know who the publisher is. They communicate through topics or channels. When a publisher sends a message to a topic, all subscribers to that topic receive the message.

### **Socket.IO and Rooms**:

In Socket.IO, **rooms** function similarly to channels or topics in a Pub/Sub model:

- **Rooms**: A room is a channel that sockets (clients) can join or leave. Messages can be sent to all clients in a specific room. This allows for broadcasting messages to specific groups of clients without broadcasting to everyone connected to the server.

- **Similarities to Pub/Sub**:
  - **Topics/Channels** in Pub/Sub correspond to **rooms** in Socket.IO.
  - **Subscribers** in Pub/Sub correspond to clients who join a room in Socket.IO.
  - **Publishers** in Pub/Sub correspond to the server or clients sending messages to a room in Socket.IO.

When a client subscribes to a topic, they join a room. When a message is published to that topic, it is broadcast to all clients in the room. This is a key feature that allows Socket.IO to efficiently handle real-time communication in scenarios where only certain clients should receive specific messages.

---

## **Part 2: Setting Up the Environment**

### **Instructions**:
1. **Install Flask and Socket.IO**:
   - Ensure you have Python installed (version 3.x).
   - Install Flask:
     ```bash
     pip install Flask
     ```
   - Install Flask-SocketIO:
     ```bash
     pip install flask-socketio
     ```
   - Install requests:
     ```bash
     pip install requests
     ``` 

2. **Set Up Flask Application**:
   - Create a directory for your project.
   - Inside the project directory, create a Python file named `server.py`.

### **Task**:
- Set up a basic Flask server with Socket.IO to handle real-time communication.

---

## **Part 3: Creating the Pub/Sub Server**

### **Instructions**:
- Implement the server to handle publishing messages and managing subscriptions.

### **Task**:
1. **Write the Server Code**:
   - Open `server.py` and implement the server code:

     ```python
     from flask import Flask, request
     from flask_socketio import SocketIO, join_room, leave_room

     app = Flask(__name__)
     socketio = SocketIO(app)

     # In-memory storage for topics and their subscribers
     topics = {}

     @app.route('/')
     def index():
         return "Pub/Sub Example with SocketIO"

     # Endpoint for publishing messages to a topic
     @app.route('/publish', methods=['POST'])
     def publish():
         data = request.json
         topic = data.get('topic')
         message = data.get('message')
         
         if topic in topics:
             # Emit the message to all subscribers in the room corresponding to the topic
             socketio.emit(topic, {'message': message}, room=topic)
             return f"Message published to topic '{topic}'", 200
         else:
             return f"Topic '{topic}' does not exist", 404

     @socketio.on('subscribe')
     def handle_subscribe(data):
         topic = data.get('topic')
         if topic not in topics:
             topics[topic] = []

         # Add the client to the topic's room
         join_room(topic)
         topics[topic].append(request.sid)
         print(f"Client {request.sid} subscribed to topic '{topic}'")

     @socketio.on('unsubscribe')
     def handle_unsubscribe(data):
         topic = data.get('topic')
         if topic in topics and request.sid in topics[topic]:
             topics[topic].remove(request.sid)

             # Remove the client from the topic's room
             leave_room(topic)
             print(f"Client {request.sid} unsubscribed from topic '{topic}'")

     @socketio.on('disconnect')
     def handle_disconnect():
         # Clean up any leftover subscriptions when a client disconnects
         for topic, subscribers in topics.items():
             if request.sid in subscribers:
                 subscribers.remove(request.sid)
                 leave_room(topic)
                 print(f"Client {request.sid} disconnected and was removed from topic '{topic}'")

     if __name__ == '__main__':
         socketio.run(app, host='0.0.0.0', port=5000)
     ```

2. **Run the Server**:
   - Run the server using the command:
     ```bash
     python server.py
     ```

---

## **Part 4: Implementing the Subscriber Client**

### **Instructions**:
- Create a client that can subscribe to topics and handle incoming messages.

### **Task**:
1. **Create a Subscriber Client Application**:
   - In the same project directory, create a Python file named `subscriber.py`.
   - Implement the client code:

   ```python
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

     ```

2. **Run the Client**:
   - Run the client using the command:
     ```bash
     python subscriber.py
     ```

---

## **Part 5: Implementing the Publisher Client**
### **Instructions**:
- Create a publisher client that can publish to topics using requests.

### **Task**:
1. **Create a Publisher Client Application**:
   - In the same project directory, create a Python file named `publisher.py`.
   - Implement the publisher client code:
   ```python
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

   ```
   
2. **Run the Client**:
   - Run the client using the command:
     ```bash
     python publisher.py
     ```
   
### **Instructions**:
- Test the Pub/Sub system by publishing messages to topics and spawning multiple subscriber processes.

---

## **Helpful Resources**

For further reading and additional help, you can refer to the following resources:

- **[Pub Sub Implementation in Python](https://arjancodes.com/blog/publish-subscribe-pattern-in-python/)**: Implementation of Pub Sub Architecture in Python
- **[Socket.IO Documentation](https://socket.io/docs/)**: Official documentation for Socket.IO, including usage examples
- **[Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)**: Detailed documentation for integrating Socket.IO with Flask
