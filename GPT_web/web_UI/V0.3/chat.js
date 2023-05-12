
const chatbox = document.getElementById("chatbox");
const input = document.getElementById("input");





input.addEventListener("keydown", function(event) {
    
  
  if (event.key === "Enter") {
    const message = input.value.trim();


    if (message) {
      const newMessage = document.createElement("div");
      newMessage.textContent = message;
      newMessage.classList.add("chat_user_style");
      chatbox.appendChild(newMessage);
      

      input.value = "";
      chat.scrollTop = chat.scrollHeight;
    }
  }
});