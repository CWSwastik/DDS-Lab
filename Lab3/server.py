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
