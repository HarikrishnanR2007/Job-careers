const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");


function addMessage(text, type) {

    const message = document.createElement("div");

    message.classList.add("message");
    message.classList.add(type);

    message.innerText = text;

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function sendMessage() {

    const message = input.value.trim();

    if (message === "") {
        return;
    }

    // Show user message
    addMessage(message, "user");

    input.value = "";


    // Send message to Flask
    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });


    const data = await response.json();


    // Show bot response
    addMessage(data.reply, "bot");
}


input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        sendMessage();

    }

});