const socket = new WebSocket("ws://192.168.1.105:8080");
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const inputTemp = document.getElementById("inputTemperature");
const inputMod = document.getElementById("inputModel");
const inputTkn = document.getElementById("inputToken");

let chatHistory = [];

function loadChatHistory() {
  const storedChatHistory = localStorage.getItem("chatHistory");
  if (storedChatHistory) {
    chatHistory = JSON.parse(storedChatHistory);
    chatHistory.forEach((message) => {
      const newMessage = document.createElement("div");
      newMessage.textContent = message.content;
      newMessage.classList.add(
        message.type === "sent" ? "chat_GPT_style" : "chat_user_style"
      );
      chat.appendChild(newMessage);
    });
    chat.scrollTop = chat.scrollHeight;
  }
}
loadChatHistory();



socket.onopen = function(event) {
  console.log("Connection opened.", event);
};

socket.onclose = function(event) {
  console.log("Connection closed.", event);
};


socket.onmessage = function(event) {
  console.log("Received message from server: ", event.data);
  const newMessage = document.createElement("div");
  newMessage.textContent = event.data;
  newMessage.classList.add("chat_user_style");
  chat.appendChild(newMessage);
  chat.scrollTop = chat.scrollHeight;

  chatHistory.push({ type: "received", content: event.data });
  localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
};


input.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    const message = input.value.trim();
    const inputTemperature = inputTemp.value.trim();
    const inputModel = inputMod.value.trim();
    const inputToken = inputTkn.value.trim();


    if (message) {
      const newMessage = document.createElement("div");
      newMessage.textContent = message;
      newMessage.classList.add("chat_GPT_style");
      chat.appendChild(newMessage);

      // Send the message to the server
      chatHistory.push({ type: "sent", content: message });
      localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
      socket.send(JSON.stringify({message, inputTemperature, inputModel, inputToken}));
      

      input.value = "";
      chat.scrollTop = chat.scrollHeight;
    }
  }
});