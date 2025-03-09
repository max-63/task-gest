const messagesElement = document.getElementById("messages-data");
const messages = JSON.parse(messagesElement.dataset.messages);
console.log(messages);
messages.sort((a, b) => new Date(a.date) - new Date(b.date)); 
const messageList = document.getElementById("message-list");
messages.forEach(message => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.innerHTML = `<strong>${message.user}</strong>: ${message.texte}`;
    messageList.appendChild(messageElement);
});