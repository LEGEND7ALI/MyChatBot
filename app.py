
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv("/home/legend7ali/.env")

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#111111">
<title>PRIME AI</title>

<style>
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

body {
    background: #111;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
}

.top {
    flex-shrink: 0;
    min-height: 62px;
    background: #1c1c1c;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 16px;
    border-bottom: 1px solid #333;
}

.title {
    font-size: 21px;
    font-weight: bold;
    white-space: nowrap;
}

.buttons {
    display: flex;
    gap: 6px;
}

button {
    font-family: inherit;
    cursor: pointer;
}

.buttons button {
    background: #292929;
    color: white;
    border: 0;
    padding: 10px;
    border-radius: 8px;
    font-size: 13px;
    white-space: nowrap;
}

.buttons button:hover {
    background: #3a3a3a;
}

.history {
    display: none;
    position: fixed;
    z-index: 10;
    top: 0;
    bottom: 0;
    left: 0;
    width: 280px;
    max-width: 85vw;
    background: #181818;
    border-right: 1px solid #333;
    padding: 16px;
    overflow-y: auto;
}

.history h3 {
    margin-top: 8px;
}

.chat-item {
    background: #252525;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    cursor: pointer;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 14px;
}

.chat-item:hover {
    background: #383838;
}

.chat {
    flex: 1;
    min-height: 0;
    width: 100%;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 16px;
}

.msg {
    width: fit-content;
    max-width: min(800px, 92%);
    padding: 13px 15px;
    margin: 12px auto;
    border-radius: 13px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.6;
    font-size: 16px;
}

.user {
    background: #2563eb;
    margin-right: 0;
}

.bot {
    background: #292929;
    margin-left: 0;
}

.bottom {
    flex-shrink: 0;
    width: 100%;
    background: #1c1c1c;
    border-top: 1px solid #333;
    padding: 12px;
    padding-bottom: max(12px, env(safe-area-inset-bottom));
}

.box {
    display: flex;
    gap: 8px;
    width: 100%;
    max-width: 850px;
    margin: auto;
}

textarea {
    flex: 1;
    min-width: 0;
    height: 50px;
    padding: 14px 12px;
    background: #292929;
    color: white;
    border: 1px solid #444;
    border-radius: 12px;
    resize: none;
    outline: none;
    font-family: inherit;
    font-size: 16px;
}

textarea:focus {
    border-color: #2563eb;
}

.send {
    flex-shrink: 0;
    padding: 0 20px;
    background: #2563eb;
    color: white;
    border: 0;
    border-radius: 12px;
    font-size: 15px;
}

.send:disabled {
    opacity: 0.6;
}

@media (max-width: 600px) {
    .top {
        min-height: auto;
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
        padding: 10px;
    }

    .title {
        font-size: 20px;
    }

    .buttons {
        width: 100%;
        gap: 5px;
    }

    .buttons button {
        flex: 1;
        min-width: 0;
        padding: 11px 2px;
        font-size: 12px;
    }

    .chat {
        padding: 10px;
    }

    .msg {
        max-width: 96%;
        padding: 12px;
        margin-top: 9px;
        margin-bottom: 9px;
        font-size: 16px;
    }

    .bottom {
        padding: 9px;
        padding-bottom: max(9px, env(safe-area-inset-bottom));
    }

    .box {
        gap: 7px;
    }

    textarea {
        height: 48px;
        padding: 13px 10px;
        font-size: 16px;
    }

    .send {
        padding: 0 15px;
        font-size: 14px;
    }
}
</style>
</head>

<body>

<header class="top">
    <div class="title">🤖 PRIME AI</div>

    <div class="buttons">
        <button onclick="toggleHistory()">📚 History</button>
        <button onclick="newChat()">➕ New Chat</button>
        <button onclick="clearChat()">🗑️ Clear</button>
    </div>
</header>

<aside class="history" id="history">
    <h3>Chat History</h3>
    <div id="historyList"></div>
    <button onclick="toggleHistory()">Close History</button>
</aside>

<main class="chat" id="chat"></main>

<footer class="bottom">
    <div class="box">
        <textarea
            id="msg"
            placeholder="Message your AI..."
            aria-label="Message your AI"
            onkeydown="key(event)"
        ></textarea>
        <button class="send" id="sendBtn" onclick="send()">Send</button>
    </div>
</footer>

<script>
let currentChat = [];
let currentChatId = null;
let sending = false;
let chats = [];

try {
    chats = JSON.parse(localStorage.getItem("myChats") || "[]");
    if (!Array.isArray(chats)) chats = [];
} catch (e) {
    chats = [];
}

function scrollBottom() {
    const area = document.getElementById("chat");
    area.scrollTop = area.scrollHeight;
}

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "msg " + type;
    div.textContent = text;
    document.getElementById("chat").appendChild(div);
    scrollBottom();
    return div;
}

async function send() {
    if (sending) return;

    const input = document.getElementById("msg");
    const sendButton = document.getElementById("sendBtn");
    const text = input.value.trim();

    if (!text) return;

    addMessage(text, "user");
    currentChat.push({type: "user", text: text});
    input.value = "";

    sending = true;
    sendButton.disabled = true;

    const thinking = addMessage("Thinking...", "bot");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: text})
        });

        const data = await response.json();

        thinking.textContent =
            data.response || "No response received.";

        currentChat.push({
            type: "bot",
            text: thinking.textContent
        });

        saveCurrentChat();

    } catch (error) {
        thinking.textContent =
            "Connection error. Please try again.";
    } finally {
        sending = false;
        sendButton.disabled = false;
        scrollBottom();
        input.focus();
    }
}

function key(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        send();
    }
}

function newChat() {
    if (sending) return;

    saveCurrentChat();
    currentChat = [];
    currentChatId = null;
    document.getElementById("chat").innerHTML = "";
    document.getElementById("history").style.display = "none";
    document.getElementById("msg").focus();
}

function clearChat() {
    if (sending) return;

    currentChat = [];
    currentChatId = null;
    document.getElementById("chat").innerHTML = "";
}

function saveCurrentChat() {
    if (currentChat.length === 0) return;

    const first = currentChat.find(m => m.type === "user");
    if (!first) return;

    const messages = currentChat.map(m => ({
        type: m.type,
        text: m.text
    }));

    let index = chats.findIndex(c => c.id === currentChatId);

    if (currentChatId === null || index === -1) {
        currentChatId = Date.now();

        chats.push({
            id: currentChatId,
            title: first.text.substring(0, 35),
            messages: messages
        });
    } else {
        chats[index].messages = messages;
        chats[index].title = first.text.substring(0, 35);
    }

    try {
        localStorage.setItem("myChats", JSON.stringify(chats));
    } catch (error) {
        console.log("Could not save chat history.");
    }

    loadHistory();
}

function loadHistory() {
    const list = document.getElementById("historyList");
    list.innerHTML = "";

    chats.slice().reverse().forEach(c => {
        const item = document.createElement("div");
        item.className = "chat-item";
        item.textContent = c.title || "New Chat";

        item.onclick = function() {
            openChat(c.id);
        };

        list.appendChild(item);
    });
}

function openChat(id) {
    if (sending) return;

    const selected = chats.find(c => c.id === id);
    if (!selected) return;

    currentChatId = id;
    currentChat = selected.messages.map(m => ({
        type: m.type,
        text: m.text
    }));

    document.getElementById("chat").innerHTML = "";

    currentChat.forEach(m => {
        addMessage(m.text, m.type);
    });

    document.getElementById("history").style.display = "none";
    scrollBottom();
}

function toggleHistory() {
    const panel = document.getElementById("history");

    if (panel.style.display === "block") {
        panel.style.display = "none";
    } else {
        panel.style.display = "block";
        loadHistory();
    }
}

loadHistory();
</script>

</body>
</html>
'''


@app.route("/")
def home():
    return HTML


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please type a message."
        }), 400

    if not GROQ_API_KEY:
        return jsonify({
            "response": "Groq API key missing. Check your .env file."
        }), 500

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        return jsonify({"response": reply})

    except Exception:
        app.logger.exception("Groq request failed")
        return jsonify({
            "response": "Groq connection failed. Please try again."
        }), 502
