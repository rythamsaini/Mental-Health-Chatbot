import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key)

# --------- USER AUTH ---------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('register'))
        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users.insert_one({'username': request.form['username'], 'password': hashpass})
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('login.html', register=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username': request.form['username']})
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials!')
            return redirect(url_for('login'))
    return render_template('login.html', register=False)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --------- CHAT ---------
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@app.route('/get_response', methods=['POST'])
def get_response():
    if 'username' not in session:
        return jsonify({'response': "Unauthorized"}), 401
    user_message = request.json.get('message', '')
    # Save user message to MongoDB
    mongo.db.messages.insert_one({
        'username': session['username'],
        'message': user_message,
        'is_bot': False
    })
    # Call Groq API with Llama3
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a supportive mental health assistant. Be empathetic, provide helpful advice, and suggest professional help if needed."},
            {"role": "user", "content": user_message}
        ],
        model="llama3-70b-8192"
    )
    bot_reply = chat_completion.choices[0].message.content
    # Save bot reply to MongoDB
    mongo.db.messages.insert_one({
        'username': session['username'],
        'message': bot_reply,
        'is_bot': True
    })
    return jsonify({'response': bot_reply})

# --------- ABOUT PAGE ---------
@app.route('/about')
def about():
    return render_template('about.html')

# --------- RESOURCES PAGE ---------
@app.route('/resources')
def resources():
    return render_template('resources.html')

# --------- HOME ---------
@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

