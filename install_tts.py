<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🎀 Aiko-Chan - Secure Anime Chatbot</title>
    <style>
        /* Anime Theme */
        :root {
            --anime-pink: #ff6b93;
            --anime-purple: #9d65c9;
            --anime-blue: #6bb5ff;
            --anime-yellow: #ffd166;
            --bg-gradient: linear-gradient(135deg, #fff0f8 0%, #f0f0ff 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --text-dark: #333344;
            --shadow-soft: 0 8px 32px rgba(255, 107, 147, 0.15);
            --shadow-strong: 0 12px 48px rgba(157, 101, 201, 0.2);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
        }
        
        body {
            background: var(--bg-gradient);
            color: var(--text-dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        /* Authentication Screens */
        .auth-container {
            background: var(--card-bg);
            padding: 40px;
            border-radius: 25px;
            box-shadow: var(--shadow-strong);
            width: 100%;
            max-width: 500px;
            margin-top: 50px;
            border: 2px solid rgba(255, 107, 147, 0.1);
            text-align: center;
        }
        
        .auth-title {
            font-size: 2.5rem;
            background: linear-gradient(45deg, var(--anime-pink), var(--anime-purple));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 20px;
        }
        
        .auth-subtitle {
            color: var(--anime-purple);
            margin-bottom: 30px;
            opacity: 0.8;
        }
        
        .auth-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        .auth-tab {
            flex: 1;
            padding: 15px;
            background: #f8f9ff;
            border: 2px solid #e6e9ff;
            border-radius: 15px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .auth-tab.active {
            background: linear-gradient(135deg, var(--anime-pink), var(--anime-purple));
            color: white;
            border-color: var(--anime-pink);
        }
        
        .auth-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            text-align: left;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-dark);
        }
        
        .form-input {
            width: 100%;
            padding: 16px 20px;
            background: #f8f9ff;
            border: 2px solid #e6e9ff;
            border-radius: 15px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--anime-pink);
            background: white;
            box-shadow: 0 0 0 3px rgba(255, 107, 147, 0.1);
        }
        
        .auth-btn {
            padding: 18px;
            background: linear-gradient(135deg, var(--anime-pink), var(--anime-purple));
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .auth-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(255, 107, 147, 0.3);
        }
        
        .auth-error {
            color: #ff4757;
            background: rgba(255, 71, 87, 0.1);
            padding: 12px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        .auth-success {
            color: #2ed573;
            background: rgba(46, 213, 115, 0.1);
            padding: 12px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        /* Chat Interface (Initially Hidden) */
        #chatInterface {
            display: none;
            width: 100%;
            max-width: 1000px;
        }
        
        /* User Info Bar */
        .user-bar {
            background: var(--card-bg);
            padding: 15px 25px;
            border-radius: 20px;
            box-shadow: var(--shadow-soft);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .user-avatar {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--anime-pink), var(--anime-purple));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.2rem;
        }
        
        .user-details {
            flex: 1;
        }
        
        .username {
            font-weight: 700;
            color: var(--text-dark);
            font-size: 1.1rem;
        }
        
        .user-email {
            color: #666;
            font-size: 0.9rem;
        }
        
        .logout-btn {
            padding: 10px 20px;
            background: rgba(255, 107, 147, 0.1);
            color: var(--anime-pink);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .logout-btn:hover {
            background: var(--anime-pink);
            color: white;
        }
        
        /* Voice Selection */
        .voice-selector {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-soft);
        }
        
        .voice-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .voice-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s;
            border: 3px solid transparent;
            text-align: center;
        }
        
        .voice-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-strong);
        }
        
        .voice-card.active {
            border-color: var(--anime-pink);
            background: linear-gradient(135deg, rgba(255, 107, 147, 0.05), rgba(157, 101, 201, 0.05));
        }
        
        .voice-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: block;
        }
        
        .voice-name {
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        /* Chat Container */
        .chat-container {
            background: var(--card-bg);
            border-radius: 20px;
            box-shadow: var(--shadow-strong);
            overflow: hidden;
            margin-bottom: 30px;
        }
        
        .chat-messages {
            height: 400px;
            padding: 25px;
            overflow-y: auto;
            background: linear-gradient(180deg, #fff9fd 0%, #f9f7ff 100%);
        }
        
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255, 107, 147, 0.05);
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: linear-gradient(var(--anime-pink), var(--anime-purple));
            border-radius: 4px;
        }
        
        /* Message Bubbles */
        .message {
            display: flex;
            gap: 15px;
            max-width: 80%;
            margin-bottom: 20px;
            animation: slideIn 0.3s ease-out;
        }
        
        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
            margin-left: auto;
        }
        
        .avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }
        
        .bot .avatar {
            background: linear-gradient(135deg, var(--anime-pink), var(--anime-purple));
            color: white;
        }
        
        .user .avatar {
            background: linear-gradient(135deg, var(--anime-blue), var(--anime-yellow));
            color: var(--text-dark);
        }
        
        .message-content {
            padding: 15px 20px;
            border-radius: 18px;
            max-width: 100%;
            word-wrap: break-word;
        }
        
        .bot .message-content {
            background: white;
            border: 2px solid rgba(255, 107, 147, 0.2);
            border-radius: 18px 18px 18px 5px;
        }
        
        .user .message-content {
            background: linear-gradient(135deg, rgba(107, 181, 255, 0.1), rgba(255, 209, 102, 0.1));
            border: 2px solid rgba(107, 181, 255, 0.3);
            border-radius: 18px 18px 5px 18px;
        }
        
        .message-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #888;
            margin-top: 10px;
        }
        
        /* Input Area */
        .input-area {
            padding: 25px;
            background: white;
            border-top: 2px solid rgba(255, 107, 147, 0.1);
        }
        
        .input-row {
            display: flex;
            gap: 15px;
        }
        
        #messageInput {
            flex: 1;
            padding: 18px 25px;
            background: #f8f9ff;
            border: 2px solid #e6e9ff;
            border-radius: 15px;
            font-size: 1rem;
            resize: none;
            min-height: 60px;
        }
        
        #messageInput:focus {
            outline: none;
            border-color: var(--anime-pink);
        }
        
        .chat-btn {
            padding: 18px 32px;
            background: linear-gradient(135deg, var(--anime-pink), var(--anime-purple));
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            min-width: 150px;
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .auth-container {
                padding: 30px 20px;
            }
            
            .voice-grid {
                grid-template-columns: 1fr;
            }
            
            .user-bar {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <!-- Authentication Screen -->
    <div class="auth-container" id="authContainer">
        <h1 class="auth-title">AIKO-CHAN</h1>
        <div class="auth-subtitle">Secure Anime Chatbot with Gemini AI</div>
        
        <div class="auth-tabs">
            <div class="auth-tab active" id="loginTab">Login</div>
            <div class="auth-tab" id="registerTab">Register</div>
        </div>
        
        <!-- Login Form -->
        <form class="auth-form" id="loginForm" style="display: block;">
            <div class="form-group">
                <label class="form-label">Username</label>
                <input type="text" class="form-input" id="loginUsername" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password</label>
                <input type="password" class="form-input" id="loginPassword" required>
            </div>
            <button type="submit" class="auth-btn">Login</button>
        </form>
        
        <!-- Register Form -->
        <form class="auth-form" id="registerForm" style="display: none;">
            <div class="form-group">
                <label class="form-label">Username</label>
                <input type="text" class="form-input" id="regUsername" required>
            </div>
            <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-input" id="regEmail" required>
            </div>
            <div class="form-group">
                <label class="form-label">Password</label>
                <input type="password" class="form-input" id="regPassword" required>
            </div>
            <button type="submit" class="auth-btn">Create Account</button>
        </form>
        
        <div class="auth-error" id="authError"></div>
        <div class="auth-success" id="authSuccess"></div>
    </div>
    
    <!-- Chat Interface (Initially Hidden) -->
    <div id="chatInterface">
        <!-- User Info Bar -->
        <div class="user-bar">
            <div class="user-info">
                <div class="user-avatar" id="userAvatar">A</div>
                <div class="user-details">
                    <div class="username" id="displayUsername">Loading...</div>
                    <div class="user-email" id="displayEmail">Loading...</div>
                </div>
            </div>
            <button class="logout-btn" id="logoutBtn">Logout</button>
        </div>
        
        <!-- Voice Selection -->
        <div class="voice-selector">
            <h3 style="color: var(--anime-pink); margin-bottom: 15px;">🎭 Choose Aiko's Personality</h3>
            <div class="voice-grid" id="voiceGrid">
                <!-- Voice cards will be populated by JavaScript -->
            </div>
        </div>
        
        <!-- Chat Container -->
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <!-- Messages will appear here -->
            </div>
            <div class="input-area">
                <div class="input-row">
                    <textarea 
                        id="messageInput" 
                        placeholder="Type your message here... (Powered by Gemini 2.5 Flash)"
                        rows="2"></textarea>
                    <button class="chat-btn" id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // --- Global Variables ---
        let authToken = localStorage.getItem('auth_token');
        let currentUser = null;
        let currentVoice = 'genki';
        let currentSession = `session_${Date.now()}`;
        
        // Voice styles data
        const voiceStyles = {
            'genki': { name: 'Genki Girl 🌟', icon: '🌟' },
            'tsundere': { name: 'Tsundere 👸', icon: '👸' },
            'cute': { name: 'Kawaii 🌸', icon: '🌸' },
            'smart': { name: 'Smart 🎓', icon: '🎓' },
            'gentle': { name: 'Gentle 🍃', icon: '🍃' }
        };
        
        // --- DOM Elements ---
        const authContainer = document.getElementById('authContainer');
        const chatInterface = document.getElementById('chatInterface');
        const loginTab = document.getElementById('loginTab');
        const registerTab = document.getElementById('registerTab');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const authError = document.getElementById('authError');
        const authSuccess = document.getElementById('authSuccess');
        const userAvatar = document.getElementById('userAvatar');
        const displayUsername = document.getElementById('displayUsername');
        const displayEmail = document.getElementById('displayEmail');
        const logoutBtn = document.getElementById('logoutBtn');
        const voiceGrid = document.getElementById('voiceGrid');
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // --- Authentication Functions ---
        function showAuthError(message) {
            authError.textContent = message;
            authError.style.display = 'block';
            authSuccess.style.display = 'none';
        }
        
        function showAuthSuccess(message) {
            authSuccess.textContent = message;
            authSuccess.style.display = 'block';
            authError.style.display = 'none';
        }
        
        function clearAuthMessages() {
            authError.style.display = 'none';
            authSuccess.style.display = 'none';
        }
        
        // --- Tab Switching ---
        loginTab.addEventListener('click', () => {
            loginTab.classList.add('active');
            registerTab.classList.remove('active');
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
            clearAuthMessages();
        });
        
        registerTab.addEventListener('click', () => {
            registerTab.classList.add('active');
            loginTab.classList.remove('active');
            registerForm.style.display = 'block';
            loginForm.style.display = 'none';
            clearAuthMessages();
        });
        
        // --- Login Handler ---
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthMessages();
            
            const username = document.getElementById('loginUsername').value.trim();
            const password = document.getElementById('loginPassword').value.trim();
            
            if (!username || !password) {
                showAuthError('Please fill in all fields');
                return;
            }
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Save token and user info
                    authToken = data.token;
                    localStorage.setItem('auth_token', authToken);
                    currentUser = {
                        id: data.user_id,
                        username: data.username,
                        email: data.email
                    };
                    
                    // Switch to chat interface
                    showChatInterface();
                    loadUserProfile();
                    loadChatHistory();
                } else {
                    showAuthError(data.message);
                }
            } catch (error) {
                showAuthError('Network error. Please try again.');
                console.error('Login error:', error);
            }
        });
        
        // --- Registration Handler ---
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthMessages();
            
            const username = document.getElementById('regUsername').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const password = document.getElementById('regPassword').value.trim();
            
            // Validation
            if (username.length < 3) {
                showAuthError('Username must be at least 3 characters');
                return;
            }
            
            if (password.length < 6) {
                showAuthError('Password must be at least 6 characters');
                return;
            }
            
            if (!email.includes('@') || !email.includes('.')) {
                showAuthError('Please enter a valid email address');
                return;
            }
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showAuthSuccess('Account created successfully! Please login.');
                    // Switch to login tab
                    loginTab.click();
                    document.getElementById('loginUsername').value = username;
                    document.getElementById('loginPassword').value = '';
                } else {
                    showAuthError(data.message);
                }
            } catch (error) {
                showAuthError('Network error. Please try again.');
                console.error('Registration error:', error);
            }
        });
        
        // --- Chat Interface Functions ---
        function showChatInterface() {
            authContainer.style.display = 'none';
            chatInterface.style.display = 'block';
            
            // Initialize voice selection
            initializeVoiceSelection();
        }
        
        function showAuthInterface() {
            authContainer.style.display = 'block';
            chatInterface.style.display = 'none';
            clearAuthMessages();
        }
        
        function initializeVoiceSelection() {
            voiceGrid.innerHTML = '';
            
            for (const [key, style] of Object.entries(voiceStyles)) {
                const card = document.createElement('div');
                card.className = `voice-card ${key === currentVoice ? 'active' : ''}`;
                card.dataset.voice = key;
                card.innerHTML = `
                    <span class="voice-icon">${style.icon}</span>
                    <div class="voice-name">${style.name}</div>
                `;
                
                card.addEventListener('click', () => {
                    document.querySelectorAll('.voice-card').forEach(c => c.classList.remove('active'));
                    card.classList.add('active');
                    currentVoice = key;
                    console.log(`Voice changed to: ${key}`);
                });
                
                voiceGrid.appendChild(card);
            }
        }
        
        // --- User Profile ---
        async function loadUserProfile() {
            if (!authToken) return;
            
            try {
                const response = await fetch('/profile', {
                    headers: {
                        'Authorization': authToken
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Update display
                    displayUsername.textContent = data.profile.username;
                    displayEmail.textContent = data.profile.email;
                    
                    // Set avatar initial
                    userAvatar.textContent = data.profile.username.charAt(0).toUpperCase();
                    
                    // Load preferences
                    loadUserPreferences();
                }
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }
        
        async function loadUserPreferences() {
            try {
                const response = await fetch('/preferences', {
                    headers: { 'Authorization': authToken }
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    currentVoice = data.preferences.voice_style || 'genki';
                    initializeVoiceSelection();
                }
            } catch (error) {
                console.error('Error loading preferences:', error);
            }
        }
        
        // --- Chat History ---
        async function loadChatHistory() {
            if (!authToken) return;
            
            try {
                const response = await fetch('/history', {
                    headers: { 'Authorization': authToken }
                });
                
                const data = await response.json();
                if (data.status === 'success' && data.messages.length > 0) {
                    // Clear current messages
                    chatMessages.innerHTML = '';
                    
                    // Add messages in chronological order
                    data.messages.reverse().forEach(msg => {
                        addMessageToChat(msg.message_type, msg.content, msg.emotion);
                    });
                } else {
                    // Add welcome message
                    addMessageToChat('bot', 'Konnichiwa! I\'m Aiko-chan! Ready to chat with you! [PAUSE:800]', 'happy');
                }
            } catch (error) {
                console.error('Error loading history:', error);
                addMessageToChat('bot', 'Hello! Let\'s start chatting!', 'happy');
            }
        }
        
        // --- Chat Functions ---
        function addMessageToChat(type, content, emotion = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = type === 'bot' ? 'A' : 'You';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Clean content for display (remove tags)
            const displayContent = content.replace(/\[.*?\]/g, '').trim();
            contentDiv.textContent = displayContent;
            
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            
            const emotionSpan = document.createElement('span');
            emotionSpan.textContent = emotion ? `${emotion} • ` : '';
            
            const timeSpan = document.createElement('span');
            timeSpan.textContent = new Date().toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            metaDiv.appendChild(emotionSpan);
            metaDiv.appendChild(timeSpan);
            contentDiv.appendChild(metaDiv);
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Speak the message if it's from bot
            if (type === 'bot') {
                speakMessage(content);
            }
        }
        
        function speakMessage(text) {
            if (!('speechSynthesis' in window)) return;
            
            // Clean text for speech
            const cleanText = text.replace(/\[.*?\]/g, '').trim();
            
            const utterance = new SpeechSynthesisUtterance(cleanText);
            
            // Set voice based on current style
            const voices = speechSynthesis.getVoices();
            const femaleVoices = voices.filter(v => v.name.toLowerCase().includes('female'));
            
            if (femaleVoices.length > 0) {
                utterance.voice = femaleVoices[0];
            }
            
            // Adjust settings based on voice style
            switch(currentVoice) {
                case 'genki':
                    utterance.pitch = 1.8;
                    utterance.rate = 1.2;
                    break;
                case 'cute':
                    utterance.pitch = 2.0;
                    utterance.rate = 1.1;
                    break;
                case 'tsundere':
                    utterance.pitch = 1.4;
                    utterance.rate = 1.1;
                    break;
                default:
                    utterance.pitch = 1.5;
                    utterance.rate = 1.0;
            }
            
            utterance.volume = 1.0;
            speechSynthesis.speak(utterance);
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || !authToken) return;
            
            // Clear input
            messageInput.value = '';
            
            // Add user message to chat
            addMessageToChat('user', message);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': authToken
                    },
                    body: JSON.stringify({
                        message: message,
                        voice_style: currentVoice,
                        session_id: currentSession
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Add bot response to chat
                    addMessageToChat('bot', data.text, data.emotion);
                } else {
                    addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.', 'sad');
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addMessageToChat('bot', 'Network error. Please check your connection.', 'sad');
            }
        }
        
        // --- Logout Handler ---
        logoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/logout', {
                    method: 'POST',
                    headers: { 'Authorization': authToken }
                });
                
                // Clear local data
                localStorage.removeItem('auth_token');
                authToken = null;
                currentUser = null;
                
                // Show auth interface
                showAuthInterface();
                
                // Clear forms
                loginForm.reset();
                registerForm.reset();
                
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
        
        // --- Event Listeners ---
        sendBtn.addEventListener('click', sendMessage);
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // --- Initialize App ---
        document.addEventListener('DOMContentLoaded', () => {
            // Check if user is already logged in
            if (authToken) {
                // Verify token
                fetch('/profile', {
                    headers: { 'Authorization': authToken }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        currentUser = {
                            id: data.profile.user_id,
                            username: data.profile.username,
                            email: data.profile.email
                        };
                        showChatInterface();
                        loadUserProfile();
                        loadChatHistory();
                    } else {
                        // Invalid token
                        localStorage.removeItem('auth_token');
                        showAuthInterface();
                    }
                })
                .catch(() => {
                    showAuthInterface();
                });
            } else {
                showAuthInterface();
            }
            
            // Initialize speech synthesis voices
            if ('speechSynthesis' in window) {
                speechSynthesis.onvoiceschanged = () => {
                    console.log('Voices loaded');
                };
            }
        });
    </script>
</body>
</html>