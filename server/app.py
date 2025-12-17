from flask import Flask, session, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    recipients = db.Column(db.Text, nullable=True)

class ChatMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    typing = db.Column(db.Boolean, default=False)
    read = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    user_id = random.randint(10000000, 99999999)
    while User.query.filter_by(id=user_id).first():
        user_id = random.randint(10000000, 99999999)
    user = User(id=user_id, username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('chats'))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/chat/<int:chat_id>', methods=['GET'])
def chat(chat_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    # Check if user is in recipients
    chat_obj = Chat.query.get(chat_id)
    if not chat_obj or str(session['user_id']) not in chat_obj.recipients.split(','):
        return jsonify({'error': 'Forbidden'}), 403
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    messages_list = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        messages_list.append({
            'id': msg.id,
            'user_id': msg.user_id,
            'username': user.username,
            'profile_picture': user.profile_picture,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
        })
    return jsonify(messages_list)

@app.route('/chats', methods=['GET'])
def chats():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_chats = Chat.query.all()
    chats_query = [chat for chat in all_chats if str(session['user_id']) in chat.recipients.split(',')]
    chat_list = []
    for chat in chats_query:
        latest_msg = Message.query.filter_by(chat_id=chat.id).order_by(desc(Message.timestamp)).first()
        if chat.name:
            chat_name = chat.name
        else:
            user_ids = [int(x.strip()) for x in chat.recipients.split(',') if x.strip()]
            other_users = [User.query.get(uid).username for uid in user_ids if uid != session['user_id']]
            chat_name = ', '.join(other_users)
        chat_data = {'id': chat.id, 'name': chat_name, 'recipients': chat.recipients}
        if latest_msg:
            user = User.query.get(latest_msg.user_id)
            chat_data['latest_message'] = {
                'id': latest_msg.id,
                'user_id': latest_msg.user_id,
                'username': user.username,
                'profile_picture': user.profile_picture,
                'message': latest_msg.message,
                'timestamp': latest_msg.timestamp.isoformat() if latest_msg.timestamp else None
            }
        else:
            chat_data['latest_message'] = {
                'message': '(This chat is empty for now. Get the conversation going!)'
            }
    #returns the list of chats with latest messages
    return jsonify(chat_list)

@app.route('/create_chat', methods=['POST'])
def create_chat():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    name = data.get('name')
    message = data.get('message')
    
    # Generate random 8-digit chat_id
    chat_id = random.randint(10000000, 99999999)
    while Chat.query.get(chat_id):
        chat_id = random.randint(10000000, 99999999)
    
    # Create new chat
    chat = Chat(id=chat_id, name=name, recipients=str(session['user_id']))
    db.session.add(chat)
    
    # Add creator as member
    chat_member = ChatMember(chat_id=chat.id, user_id=session['user_id'])
    db.session.add(chat_member)
    db.session.commit()
    
    # If message provided, create message
    if message:
        new_message = Message(chat_id=chat.id, user_id=session['user_id'], message=message)
        db.session.add(new_message)
        db.session.commit()
    
    return jsonify({'success': True, 'chat_id': chat.id})

@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    chat_id = data.get('chat_id')
    message = data.get('message')
    
    if not chat_id or not message:
        return jsonify({'success': False, 'message': 'chat_id and message required'}), 400
    
    chat = Chat.query.get(chat_id)
    if not chat or str(session['user_id']) not in chat.recipients.split(','):
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    
    new_message = Message(chat_id=chat_id, user_id=session['user_id'], message=message)
    db.session.add(new_message)
    db.session.commit()
    
    message_data = {
        'id': new_message.id,
        'chat_id': chat_id,
        'user_id': new_message.user_id,
        'username': User.query.get(new_message.user_id).username,
        'profile_picture': User.query.get(new_message.user_id).profile_picture,
        'message': new_message.message,
        'timestamp': new_message.timestamp.isoformat() if new_message.timestamp else None
    }
    emit('new_message', message_data, room=str(chat_id))
    
    return jsonify({'success': True, 'message_id': new_message.id})

@socketio.on('join_chat')
def handle_join_chat(data):
    chat_id = data['chat_id']
    join_room(str(chat_id))

@socketio.on('leave_chat')
def handle_leave_chat(data):
    chat_id = data['chat_id']
    leave_room(str(chat_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)
