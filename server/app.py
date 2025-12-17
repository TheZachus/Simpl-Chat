from flask import Flask, session, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

class ChatMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

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

@app.route('/chat', methods=['GET'])
def chat():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    # Dummy data for chat messages
    messages = [
        {'id': 1, 'user': 'User1', 'message': 'Hello!'},
        {'id': 2, 'user': 'User2', 'message': 'Hi there!'}
    ]
    return jsonify(messages)

@app.route('/chats', methods=['GET'])
def chats():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    chats_query = Chat.query.all()
    chat_list = []
    for chat in chats_query:
        latest_msg = Message.query.filter_by(chat_id=chat.id).order_by(desc(Message.timestamp)).first()
        if chat.name:
            chat_name = chat.name
        else:
            members = ChatMember.query.filter_by(chat_id=chat.id).all()
            other_users = [m.user.username for m in members if m.user_id != session['user_id']]
            chat_name = ', '.join(other_users)
        chat_data = {'id': chat.id, 'name': chat_name}
        if latest_msg:
            chat_data['latest_message'] = {
                'id': latest_msg.id,
                'user_id': latest_msg.user_id,
                'message': latest_msg.message,
                'timestamp': latest_msg.timestamp.isoformat() if latest_msg.timestamp else None
            }
        else:
            chat_data['latest_message'] = {
                'message': '(This chat is empty for now. Get the conversation going!)'
            }
        chat_list.append(chat_data)
    #returns the list of chats with latest messages
    return jsonify(chat_list)

if __name__ == '__main__':
    app.run(debug=True)
