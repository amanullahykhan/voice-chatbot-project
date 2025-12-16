import sqlite3
import os
import re
import random
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from contextlib import contextmanager
from functools import wraps

# Try to import google.genai
try:
    import google.genai as genai
    USE_NEW_GENAI = True
    print("✅ Using new google.genai package")
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_GENAI = False
        print("⚠️ Using deprecated google.generativeai package")
    except ImportError:
        genai = None
        print("❌ No Gemini AI package found")

# --- Flask Configuration ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DATABASE = 'chatbot_auth.db'
TOKEN_EXPIRY_DAYS = 7

# --- Gemini AI Setup ---
def init_gemini():
    """Initialize Gemini AI"""
    if genai is None:
        print("❌ No Gemini AI package installed")
        return None
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("⚠️ WARNING: GEMINI_API_KEY not found")
        return None
    
    try:
        # For new google.genai, configuration is different
        if USE_NEW_GENAI:
            # New API format - just check if we can create a client
            # The key is passed directly to the client, not configured globally
            print("✅ Using new Gemini API format")
            return True
        else:
            # Old API format
            genai.configure(api_key=gemini_api_key)
            print("✅ Gemini AI initialized successfully")
            return True
    except Exception as e:
        print(f"⚠️ Gemini AI initialization failed: {e}")
        return None

# Initialize Gemini
gemini_available = init_gemini()

# --- Database Context Manager ---
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# --- Database Initialization ---
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # User sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,  -- 'user' or 'assistant'
                content TEXT NOT NULL,
                voice_style TEXT DEFAULT 'natural',
                emotion TEXT DEFAULT 'neutral',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                voice_style TEXT DEFAULT 'natural',
                theme TEXT DEFAULT 'light',
                auto_play_voice INTEGER DEFAULT 1,
                speech_rate FLOAT DEFAULT 1.0,
                speech_pitch FLOAT DEFAULT 1.0,
                conversation_style TEXT DEFAULT 'casual',
                use_fillers INTEGER DEFAULT 1,
                use_pauses INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_messages ON chat_messages(user_id, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation ON chat_messages(conversation_id)')
        
    print("✅ Database initialized successfully")

# --- Password Hashing ---
def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password, stored_hash):
    if not stored_hash or '$' not in stored_hash:
        return False
    salt, hash_value = stored_hash.split('$')
    return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization') or request.cookies.get('auth_token')
        
        if not auth_token:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        
        user_id = verify_session_token(auth_token)
        if not user_id:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
        
        # Store user_id in request object
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# --- Session Management ---
def create_session_token(user_id):
    token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
    
    return token

def verify_session_token(token):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id FROM user_sessions 
            WHERE session_token = ? AND expires_at > ?
        ''', (token, datetime.now()))
        
        result = cursor.fetchone()
        return result['user_id'] if result else None

# --- User Management ---
def create_user(username, email, password):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            return None, "Username or email already exists"
        
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, datetime.now()))
        
        user_id = cursor.lastrowid
        
        # Create default preferences
        cursor.execute('''
            INSERT INTO user_preferences (user_id, voice_style, theme, auto_play_voice, speech_rate, speech_pitch, conversation_style, use_fillers, use_pauses)
            VALUES (?, 'natural', 'light', 1, 1.0, 1.0, 'casual', 1, 1)
        ''', (user_id,))
        
        return user_id, None

def authenticate_user(username, password):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, password_hash FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        if not user:
            return None, "Invalid username or password"
        
        if verify_password(password, user['password_hash']):
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now(), user['id']))
            return user['id'], None
        else:
            return None, "Invalid username or password"

# --- Chat History ---
def save_chat_message(user_id, conversation_id, role, content, voice_style='natural', emotion='neutral'):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (user_id, conversation_id, role, content, voice_style, emotion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, conversation_id, role, content, voice_style, emotion))
        
        return cursor.lastrowid

def get_conversation_history(user_id, conversation_id, limit=10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content, emotion FROM chat_messages 
            WHERE user_id = ? AND conversation_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, conversation_id, limit))
        
        messages = cursor.fetchall()
        return [dict(msg) for msg in messages][::-1]  # Reverse to chronological order

# --- User Preferences ---
def get_user_preferences(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT voice_style, theme, auto_play_voice, speech_rate, speech_pitch, 
                   conversation_style, use_fillers, use_pauses
            FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        
        prefs = cursor.fetchone()
        return dict(prefs) if prefs else {
            'voice_style': 'natural',
            'theme': 'light',
            'auto_play_voice': 1,
            'speech_rate': 1.0,
            'speech_pitch': 1.0,
            'conversation_style': 'casual',
            'use_fillers': 1,
            'use_pauses': 1
        }

def update_user_preferences(user_id, **preferences):
    allowed_fields = ['voice_style', 'theme', 'auto_play_voice', 'speech_rate', 'speech_pitch', 
                      'conversation_style', 'use_fillers', 'use_pauses']
    updates = {k: v for k, v in preferences.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE user_preferences 
            SET {set_clause}, updated_at = ?
            WHERE user_id = ?
        ''', values + [datetime.now()])
        
        return cursor.rowcount > 0

# --- NATURAL VOICE SYSTEM ---
class NaturalVoiceSystem:
    """Natural human-like voice system with emotions"""
    
    VOICE_STYLES = {
        'natural': {
            'name': 'Natural Human 🗣️',
            'description': 'Normal conversational tone',
            'pitch': 1.0,
            'rate': 1.0,
            'volume': 1.0,
            'pause_duration': 0.8
        },
        'warm': {
            'name': 'Warm & Friendly 😊',
            'description': 'Friendly, caring tone with warmth',
            'pitch': 1.1,
            'rate': 0.95,
            'volume': 1.0,
            'pause_duration': 1.0
        },
        'energetic': {
            'name': 'Energetic ⚡',
            'description': 'Lively and enthusiastic',
            'pitch': 1.2,
            'rate': 1.2,
            'volume': 1.0,
            'pause_duration': 0.6
        },
        'calm': {
            'name': 'Calm & Soothing 🍃',
            'description': 'Relaxed, peaceful tone',
            'pitch': 0.9,
            'rate': 0.85,
            'volume': 0.9,
            'pause_duration': 1.2
        },
        'playful': {
            'name': 'Playful 😄',
            'description': 'Fun, light-hearted with smiles',
            'pitch': 1.15,
            'rate': 1.1,
            'volume': 1.0,
            'pause_duration': 0.7
        }
    }
    
    @staticmethod
    def get_voice_settings(style='natural'):
        """Get natural voice settings"""
        return NaturalVoiceSystem.VOICE_STYLES.get(style, NaturalVoiceSystem.VOICE_STYLES['natural'])

# --- GEMINI AI RESPONSE GENERATOR ---
class GeminiChatAssistant:
    """Gemini AI with natural conversation flow"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.conversation_styles = {
            'natural': {
                'prompt': """You are Aiko, a friendly and natural human conversational partner.
                Speak like a real person - use contractions (I'm, you're), occasional filler words, and natural pauses.
                Be empathetic, show genuine interest, and respond like you're having a real conversation.
                Keep responses conversational and avoid robotic patterns."""
            },
            'warm': {
                'prompt': """You are Aiko, a warm and caring friend.
                Speak with genuine warmth and empathy. Show you care about the conversation.
                Use comforting language and be supportive."""
            },
            'energetic': {
                'prompt': """You are Aiko, an energetic and enthusiastic friend.
                Speak with excitement and positivity! Use exclamation marks appropriately.
                Be encouraging and motivational."""
            },
            'calm': {
                'prompt': """You are Aiko, a calm and soothing presence.
                Speak slowly and clearly, with a peaceful tone.
                Be reassuring and create a relaxing atmosphere."""
            },
            'playful': {
                'prompt': """You are Aiko, a playful and fun friend.
                Use humor and light-hearted language. Tease playfully when appropriate.
                Keep things fun and engaging."""
            }
        }
    
    def generate_response(self, user_message, conversation_history, user_id, voice_style='natural'):
        """Generate natural response using Gemini AI"""
        
        style_prompt = self.conversation_styles.get(voice_style, self.conversation_styles['natural'])['prompt']
        
        # Prepare conversation context
        history_text = ""
        if conversation_history:
            for msg in conversation_history:
                speaker = "User" if msg['role'] == 'user' else "Aiko"
                history_text += f"{speaker}: {msg['content']}\n"
        
        # Construct the prompt
        prompt = f"""{style_prompt}

Previous conversation:
{history_text}

User: {user_message}

Aiko:"""
        
        try:
            if gemini_available and self.api_key:
                # Use real Gemini API
                if USE_NEW_GENAI:
                    # New API format
                    client = genai.Client(api_key=self.api_key)
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                        config={
                            'temperature': 0.9,
                            'top_p': 0.95,
                            'top_k': 40,
                            'max_output_tokens': 200,
                        }
                    )
                    bot_response = response.text
                else:
                    # Old API format
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.9,
                            'top_p': 0.95,
                            'top_k': 40,
                            'max_output_tokens': 200,
                        }
                    )
                    bot_response = response.text
                
                bot_response = self._clean_response(bot_response)
                
            else:
                # Fallback: Generate natural responses
                bot_response = self._generate_fallback_response(user_message, voice_style)
                gemini_used = False
            
            # Extract emotion from response
            emotion = self._detect_emotion(bot_response)
            
            return {
                'text': bot_response,
                'emotion': emotion,
                'voice_style': voice_style,
                'voice_name': NaturalVoiceSystem.VOICE_STYLES[voice_style]['name'],
                'is_gemini': gemini_available and bool(self.api_key),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            # Fallback response
            fallback = self._generate_fallback_response(user_message, voice_style)
            return {
                'text': fallback,
                'emotion': 'neutral',
                'voice_style': voice_style,
                'voice_name': NaturalVoiceSystem.VOICE_STYLES[voice_style]['name'],
                'is_gemini': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def _clean_response(self, text):
        """Clean and format response"""
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italics
        
        if not text.endswith(('.', '!', '?', '"', "'")):
            text = text.rstrip() + '.'
        
        return text.strip()
    
    def _detect_emotion(self, text):
        """Detect emotion from text content"""
        text_lower = text.lower()
        
        emotion_keywords = {
            'happy': ['happy', 'great', 'wonderful', 'excited', 'yay', 'smile', 'love'],
            'sad': ['sad', 'sorry', 'unfortunate', 'upset', 'tear', 'miss'],
            'excited': ['wow', 'amazing', 'fantastic', 'awesome', 'cool', '!'],
            'calm': ['peace', 'calm', 'relax', 'gentle', 'soft', 'quiet'],
            'playful': ['fun', 'joke', 'play', 'hehe', 'haha', 'wink'],
            'thoughtful': ['think', 'consider', 'perhaps', 'maybe', 'possibly']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return 'neutral'
    
    def _generate_fallback_response(self, user_message, voice_style):
        """Generate varied fallback responses"""
        user_lower = user_message.lower()
        
        # Greeting responses
        if any(word in user_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            greetings = {
                'natural': ["Hi there! How are you doing today?", "Hello! It's nice to talk with you.", "Hey! What's on your mind?"],
                'warm': ["Hello! It's so good to see you. How have you been?", "Hi there! I've been thinking about our conversations.", "Hey! I'm really glad we're talking."],
                'energetic': ["Hey!! How's it going? I'm excited to chat!", "Hi! Wow, great to hear from you!", "Hello! Let's have an awesome conversation!"],
                'calm': ["Hello... It's peaceful to talk with you.", "Hi. I hope you're having a calm day.", "Hey. Let's have a gentle conversation."],
                'playful': ["Hehe, hi there! Ready for some fun chat?", "Hey you! What mischief are we up to today?", "Hi! Let's have a playful conversation!"]
            }
            return random.choice(greetings.get(voice_style, greetings['natural']))
        
        # Question responses
        elif '?' in user_message:
            questions = {
                'natural': ["That's an interesting question. Let me think about it...", "Hmm, I'm not completely sure, but here's what I think...", "Good question! I believe..."],
                'warm': ["I appreciate you asking that. From what I understand...", "That's a thoughtful question. I feel that...", "Thanks for sharing that question with me. I think..."],
                'energetic': ["Wow, great question! I'm excited to share my thoughts...", "Awesome question! Here's what comes to mind...", "Cool question! I think..."],
                'calm': ["That's a peaceful question to consider. I believe...", "I'll ponder that quietly. It seems to me...", "A calm question deserves a thoughtful answer..."],
                'playful': ["Hehe, tricky question! Let me play with that idea...", "Fun question! I'd say...", "Ooh, interesting! I think..."]
            }
            return random.choice(questions.get(voice_style, questions['natural']))
        
        # Default varied responses
        responses = {
            'natural': [
                "I understand what you mean. That's really interesting.",
                "Thanks for sharing that with me. It gives me something to think about.",
                "I see what you're saying. That's a good point to consider.",
                "You make a good observation there. I appreciate your perspective.",
                "That's a thoughtful thing to say. I'm enjoying our conversation."
            ],
            'warm': [
                "I really appreciate you sharing that. It means a lot to hear your thoughts.",
                "Thank you for being so open. I value our conversations.",
                "That's very considerate of you to mention. I'm touched.",
                "I'm glad we can talk like this. Your perspective is important.",
                "You have a kind way of expressing yourself. I enjoy our chats."
            ],
            'energetic': [
                "Wow, that's awesome! I love hearing your thoughts!",
                "Cool! That's really exciting to hear!",
                "Fantastic! I'm so glad you mentioned that!",
                "Amazing! Your perspective is really energizing!",
                "Great point! I'm pumped about our conversation!"
            ],
            'calm': [
                "That's peaceful to consider. I appreciate the calm in your words.",
                "Thank you for the gentle thoughts. It's soothing to chat.",
                "I find comfort in our conversation. Your words are calming.",
                "That's a serene perspective. I enjoy our peaceful chats.",
                "Your gentle approach to conversation is refreshing."
            ],
            'playful': [
                "Hehe, that's fun to think about! Let's explore that idea!",
                "You have a playful perspective! I like that!",
                "That's a mischievous thought! I'm intrigued!",
                "Fun idea! Let's play with that concept!",
                "You make conversation enjoyable with your playful approach!"
            ]
        }
        
        return random.choice(responses.get(voice_style, responses['natural']))

# Initialize systems
voice_system = NaturalVoiceSystem()
chat_assistant = GeminiChatAssistant()

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if len(username) < 3:
        return jsonify({"status": "error", "message": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400
    
    user_id, error = create_user(username, email, password)
    if error:
        return jsonify({"status": "error", "message": error}), 400
    
    token = create_session_token(user_id)
    
    return jsonify({
        "status": "success",
        "message": "Registration successful",
        "token": token,
        "user_id": user_id,
        "username": username
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    user_id, error = authenticate_user(username, password)
    if error:
        return jsonify({"status": "error", "message": error}), 401
    
    token = create_session_token(user_id)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
    
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "token": token,
        "user_id": user_id,
        "username": user['username'],
        "email": user['email']
    })

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get user profile information"""
    user_id = request.user_id
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, created_at, last_login FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
    
    return jsonify({
        "status": "success",
        "profile": dict(user)
    })

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat with natural responses"""
    user_id = request.user_id
    data = request.get_json()
    user_message = data.get('message', '').strip()
    voice_style = data.get('voice_style', 'natural')
    conversation_id = data.get('conversation_id', f"conv_{datetime.now().timestamp()}")
    
    if not user_message:
        return jsonify({"status": "error", "message": "No message provided"}), 400
    
    # Get conversation history for context
    history = get_conversation_history(user_id, conversation_id, limit=5)
    
    # Save user message
    save_chat_message(user_id, conversation_id, 'user', user_message, voice_style)
    
    # Generate response using Gemini AI
    response_data = chat_assistant.generate_response(user_message, history, user_id, voice_style)
    
    # Save bot response with emotion
    save_chat_message(user_id, conversation_id, 'assistant', response_data['text'], 
                     voice_style, response_data['emotion'])
    
    # Get voice settings
    voice_settings = voice_system.get_voice_settings(voice_style)
    
    # Add user's custom speech preferences
    user_prefs = get_user_preferences(user_id)
    voice_settings['user_rate'] = user_prefs.get('speech_rate', 1.0)
    voice_settings['user_pitch'] = user_prefs.get('speech_pitch', 1.0)
    
    return jsonify({
        "status": "success",
        **response_data,
        "voice_settings": voice_settings,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "gemini_used": response_data['is_gemini']
    })

@app.route('/history', methods=['GET'])
@login_required
def get_history():
    user_id = request.user_id
    conversation_id = request.args.get('conversation_id', 'default')
    limit = request.args.get('limit', 50, type=int)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content, voice_style, emotion, created_at
            FROM chat_messages 
            WHERE user_id = ? AND conversation_id = ?
            ORDER BY created_at ASC
            LIMIT ?
        ''', (user_id, conversation_id, limit))
        
        messages = cursor.fetchall()
    
    return jsonify({
        "status": "success",
        "messages": [dict(msg) for msg in messages],
        "conversation_id": conversation_id
    })

@app.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get list of user's conversations"""
    user_id = request.user_id
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT conversation_id, MAX(created_at) as last_activity
            FROM chat_messages 
            WHERE user_id = ?
            GROUP BY conversation_id
            ORDER BY last_activity DESC
            LIMIT 20
        ''', (user_id,))
        
        conversations = cursor.fetchall()
    
    return jsonify({
        "status": "success",
        "conversations": [dict(conv) for conv in conversations]
    })

@app.route('/preferences', methods=['GET', 'PUT'])
@login_required
def preferences():
    user_id = request.user_id
    
    if request.method == 'GET':
        prefs = get_user_preferences(user_id)
        return jsonify({"status": "success", "preferences": prefs})
    
    elif request.method == 'PUT':
        data = request.get_json()
        if update_user_preferences(user_id, **data):
            return jsonify({"status": "success", "message": "Preferences updated"})
        else:
            return jsonify({"status": "error", "message": "Failed to update preferences"}), 400

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user by invalidating session token"""
    auth_token = request.headers.get('Authorization') or request.cookies.get('auth_token')
    
    if auth_token:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (auth_token,))
    
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    })

@app.route('/voices', methods=['GET'])
def get_voices():
    return jsonify({
        "status": "success",
        "voices": voice_system.VOICE_STYLES
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "success",
        "server": "running",
        "gemini_ai": "connected" if gemini_available else "disconnected",
        "features": {
            "natural_voice": True,
            "human_like_conversation": True,
            "emotion_detection": True,
            "voice_input": True,
            "gemini_responses": gemini_available
        }
    })

@app.route('/api/key', methods=['GET'])
@login_required
def get_api_key():
    """Check if API key is available"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    return jsonify({
        "status": "success",
        "has_key": bool(gemini_api_key)
    })

# --- Main Entry Point ---
if __name__ == '__main__':
    print("=" * 70)
    print("🎀 AIKO - Natural Human-Like Chatbot")
    print("✨ FEATURES:")
    print("   • Natural human-like conversation")
    print("   • Voice input support")
    print("   • User authentication")
    print("   • 5 distinct personality styles")
    print("=" * 70)
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        try:
            if os.path.exists(DATABASE):
                os.remove(DATABASE)
            init_db()
            print("✅ Database recreated successfully")
        except:
            print("❌ Failed to initialize database")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🤖 Gemini: {'Connected' if gemini_available else 'Using enhanced fallback'}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=True)