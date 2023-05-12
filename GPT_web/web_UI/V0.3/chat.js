
const chatbox = document.getElementById("chatbox");
var input = document.getElementById("input");
var enter = document.getElementById("enter")




function prossceSend(){
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


enter.addEventListener("click", function() {

  prossceSend();

});

input.addEventListener('keypress', function(event) {
  if (event.key == 'Enter' && event.shiftKey) {
    prossceSend();
  }
});