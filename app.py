from flask import Flask, request, jsonify
import os
import webbrowser
import threading
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

HTML = r'''
<!DOCTYPE html>
<html>
<head>
<title>My AI Chatbot</title>

<style>
*{box-sizing:border-box}

body{
    margin:0;
    background:#111;
    color:white;
    font-family:Arial,sans-serif;
}

.top{
    height:60px;
    background:#1c1c1c;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 18px;
    border-bottom:1px solid #333;
}

.title{
    font-size:20px;
    font-weight:bold;
}

.buttons button{
    background:#292929;
    color:white;
    border:0;
    padding:9px 12px;
    margin-left:5px;
    border-radius:8px;
    cursor:pointer;
}

.buttons button:hover{
    background:#3a3a3a;
}

.history{
    position:fixed;
    left:0;
    top:60px;
    bottom:0;
    width:230px;
    background:#181818;
    border-right:1px solid #333;
    padding:12px;
    overflow-y:auto;
    display:none;
}

.history h3{
    margin-top:5px;
}

.chat-item{
    background:#252525;
    padding:10px;
    margin:7px 0;
    border-radius:8px;
    cursor:pointer;
    overflow:hidden;
    white-space:nowrap;
    text-overflow:ellipsis;
}

.chat-item:hover{
    background:#333;
}

.chat{
    height:calc(100vh - 140px);
    overflow-y:auto;
    padding:20px;
}

.msg{
    max-width:750px;
    margin:12px auto;
    padding:14px;
    border-radius:12px;
    white-space:pre-wrap;
    line-height:1.5;
}

.user{
    background:#2563eb;
}

.bot{
    background:#292929;
}

.bottom{
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    background:#1c1c1c;
    padding:12px;
    border-top:1px solid #333;
}

.box{
    max-width:800px;
    margin:auto;
    display:flex;
    gap:8px;
}

textarea{
    flex:1;
    height:48px;
    background:#292929;
    color:white;
    border:1px solid #444;
    border-radius:10px;
    padding:12px;
    resize:none;
    outline:none;
}

.send{
    background:#2563eb;
    color:white;
    border:0;
    border-radius:10px;
    padding:0 20px;
    cursor:pointer;
}
</style>
</head>

<body>

<div class="top">

    <div class="title">🤖 My AI Chatbot</div>

    <div class="buttons">
        <button onclick="toggleHistory()">📚 History</button>
        <button onclick="newChat()">➕ New Chat</button>
        <button onclick="clearChat()">🗑️ Clear</button>
    </div>

</div>

<div class="history" id="history">

    <h3>Chat History</h3>

    <div id="historyList"></div>

</div>

<div class="chat" id="chat"></div>

<div class="bottom">

    <div class="box">

        <textarea
            id="msg"
            placeholder="Message your AI..."
            onkeydown="key(event)"
        ></textarea>

        <button class="send" onclick="send()">Send</button>

    </div>

</div>

<script>

let currentChat = [];
let chats = JSON.parse(localStorage.getItem("myChats") || "[]");

function add(text,type){

    let d = document.createElement("div");

    d.className = "msg " + type;

    d.textContent = text;

    document.getElementById("chat").appendChild(d);

    d.scrollIntoView();

}

function send(){

    let input = document.getElementById("msg");

    let text = input.value.trim();

    if(!text) return;

    add(text,"user");

    currentChat.push({
        type:"user",
        text:text
    });

    input.value = "";

    add("Thinking...","bot");

    fetch("/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            message:text
        })

    })

    .then(r => r.json())

    .then(data => {

        let bots = document.querySelectorAll(".bot");

        bots[bots.length-1].textContent = data.response;

        currentChat.push({
            type:"bot",
            text:data.response
        });

        saveCurrentChat();

    })

    .catch(() => {

        let bots = document.querySelectorAll(".bot");

        bots[bots.length-1].textContent =
        "Connection error. Please try again.";

    });

}

function key(e){

    if(e.key === "Enter" && !e.shiftKey){

        e.preventDefault();

        send();

    }

}

function newChat(){

    saveCurrentChat();

    currentChat = [];

    window.currentChatId = null;

    document.getElementById("chat").innerHTML = "";

    document.getElementById("msg").focus();

}

function clearChat(){

    currentChat = [];

    document.getElementById("chat").innerHTML = "";

}

function saveCurrentChat(){

    if(currentChat.length === 0) return;

    let firstMessage = currentChat.find(x => x.type === "user");

    if(!firstMessage) return;

    let title = firstMessage.text.substring(0,35);

    let existing = chats.findIndex(
        x => x.id === window.currentChatId
    );

    if(!window.currentChatId){

        window.currentChatId = Date.now();

        chats.push({

            id:window.currentChatId,

            title:title,

            messages:currentChat

        });

    }else{

        if(existing >= 0){

            chats[existing].messages = currentChat;

        }

    }

    localStorage.setItem(
        "myChats",
        JSON.stringify(chats)
    );

    loadHistory();

}

function loadHistory(){

    let list = document.getElementById("historyList");

    list.innerHTML = "";

    chats.slice().reverse().forEach(chat => {

        let item = document.createElement("div");

        item.className = "chat-item";

        item.textContent = chat.title;

        item.onclick = function(){

            openChat(chat.id);

        };

        list.appendChild(item);

    });

}

function openChat(id){

    let selected = chats.find(x => x.id === id);

    if(!selected) return;

    window.currentChatId = id;

    currentChat = selected.messages;

    document.getElementById("chat").innerHTML = "";

    currentChat.forEach(message => {

        add(
            message.text,
            message.type
        );

    });

}

function toggleHistory(){

    let panel = document.getElementById("history");

    if(panel.style.display === "block"){

        panel.style.display = "none";

    }else{

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

    data = request.get_json()

    message = data["message"]

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ]

        )

        reply = response.choices[0].message.content

        return jsonify({
            "response": reply
        })

    except Exception as e:

        print("Groq Error:", e)

        return jsonify({
            "response":
            "Groq se connection nahi ho raha. Please try again."
        })


def open_browser():

    webbrowser.open(
        "http://127.0.0.1:5000"
    )


if __name__ == "__main__":

    threading.Timer(
        1.5,
        open_browser
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
