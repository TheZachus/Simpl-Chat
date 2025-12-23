from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

current_rooms = {}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recipients = db.Column(db.Text, nullable=False) 

class ChatMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    read = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if not current_user.is_authenticated:
        message = request.args.get('message')
        return render_template('index.html', title="Simple Chat", message=message)
    return redirect(url_for('get_chats'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', title="Register")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        if password != confirm_password:
            return render_template('register.html', title="Register", error="Passwords do not match")
        if not username or not password:
            return render_template('register.html', title="Register", error="Username and password required")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', title="Register", error="Username already exists")
        user_id = random.randint(10000000, 99999999)
        while User.query.filter_by(id=user_id).first():
            user_id = random.randint(10000000, 99999999)
        user = User(id=user_id, username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('get_chats'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title="Login")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('get_chats'))
        else:
            return render_template('login.html', title="Login", error="Invalid credentials")

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index', message="Logged out successfully."))

@app.route('/chat/<int:chat_id>', methods=['GET'])
@login_required

def chat(chat_id):
    # Check if user is in recipients
    chat_obj = Chat.query.get(chat_id)
    if not chat_obj or str(current_user.id) not in chat_obj.recipients.split(','):
        return redirect(url_for('get_chats'))
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    messages_list = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        messages_list.append({
            'id': msg.id,
            'user_id': msg.user_id,
            'username': user.username,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
        })
    return render_template('chat-room.html', chat_id=chat_id, messages=messages_list)

@app.route('/chats', methods=['GET'])
@login_required
def get_chats():
    current_user_id = current_user.id

    # Filter chats where current_user_id is in the recipients string
    chats_query = Chat.query.filter(Chat.recipients.contains(str(current_user_id))).all()

    chat_list = []
    for chat in chats_query:
        latest_msg = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
        
        # Get read status from ChatMember
        chat_member = ChatMember.query.filter_by(chat_id=chat.id, user_id=current_user_id).first()
        read_status = chat_member.read if chat_member else False
        
        if not chat.name:
            recipient_ids = [int(x) for x in chat.recipients.split(',') if x.strip()]
            other_users = User.query.filter(User.id.in_(recipient_ids), User.id != current_user_id).all()
            chat_name = ', '.join([u.username for u in other_users])
        else:
            chat_name = chat.name

        chat_data = {
            'id': chat.id,
            'name': chat_name,
            'read': read_status,
            'latest_message': {
                'message': latest_msg.message if latest_msg else 'Empty chat',
                'username': User.query.get(latest_msg.user_id).username if latest_msg else None,
                'timestamp': latest_msg.timestamp.isoformat() if latest_msg and latest_msg.timestamp else None
            }
        }
        chat_list.append(chat_data)

    return render_template('view-chats.html', chats=chat_list)

@app.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Search for users matching the query (excluding current user)
    # Use func.lower for case-insensitive search (works with SQLite)
    from sqlalchemy import func
    users = User.query.filter(
        func.lower(User.username).like(f'%{query.lower()}%'),
        User.id != current_user.id
    ).limit(5).all()
    
    results = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(results)

@app.route('/create_chat', methods=['GET', 'POST'])
@login_required
def create_chat():
    if request.method == 'GET':
        return render_template('create-chat.html', title="Create Chat")
    
    name = request.form.get('name')
    message = request.form.get('message')
    selected_users = request.form.getlist('selected_users')  # Get list of selected user IDs
    
    # Check if no users are selected
    if not selected_users:
        return render_template('create-chat.html', title="Create Chat", message="No users selected.")
    
    # Combine current user with selected users
    recipient_ids = [str(current_user.id)]
    if selected_users:
        recipient_ids.extend(selected_users)
    
    chat_id = random.randint(10000000, 99999999)
    while Chat.query.get(chat_id):
        chat_id = random.randint(10000000, 99999999)
    
    # Create chat with all recipients
    chat = Chat(id=chat_id, name=name, recipients=','.join(recipient_ids))
    db.session.add(chat)
    
    # Add ChatMember records for all recipients
    for user_id in recipient_ids:
        chat_member = ChatMember(chat_id=chat.id, user_id=int(user_id))
        db.session.add(chat_member)
    
    db.session.commit()
    
    if message:
        new_message = Message(chat_id=chat.id, user_id=current_user.id, message=message)
        db.session.add(new_message)
        db.session.commit()
    
    return redirect(url_for('chat', chat_id=chat.id))

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    chat_id = request.form.get('chat_id')
    message = request.form.get('message')
    
    if not chat_id or not message:
        return redirect(url_for('chat', chat_id=chat_id, error="Chat ID and message required"))
    
    chat = Chat.query.get(chat_id)
    if not chat or str(current_user.id) not in chat.recipients.split(','):
        return redirect(url_for('get_chats'))

    new_message = Message(chat_id=chat_id, user_id=current_user.id, message=message)
    db.session.add(new_message)
    db.session.commit()
    
    emit('new_message', {
        'id': new_message.id,
        'chat_id': chat_id,
        'user_id': new_message.user_id,
        'username': User.query.get(new_message.user_id).username,
        'message': new_message.message,
        'timestamp': new_message.timestamp.isoformat() if new_message.timestamp else None
    }, room=str(chat_id))
    
    return redirect(url_for('chat', chat_id=chat.id))

@socketio.on('join_chat')
@login_required
def handle_join_chat(data):
    chat_id = data['chat_id']
    sid = request.sid
    if sid in current_rooms:
        leave_room(str(current_rooms[sid]))
    join_room(str(chat_id))
    current_rooms[sid] = chat_id

@socketio.on('leave_chat')
@login_required
def handle_leave_chat(data):
    chat_id = data['chat_id']
    sid = request.sid
    leave_room(str(chat_id))
    if sid in current_rooms:
        del current_rooms[sid]

if __name__ == "__main__":
    app.run(debug=True)