const socket = new WebSocket("ws://127.0.0.1:8080");
const inputTemp = document.getElementById("inputTemperature");
const inputTkn = document.getElementById("inputToken");
const inputSnr = document.getElementById("inputSnr");
// const inputSnrCus = document.getElementById("inputSnrCus");
const inputKey = document.getElementById("inputKey");
// const selectElement = document.getElementById('mySelect');
const chatbox = document.getElementById("chatbox");
var input = document.getElementById("input");

var enter = document.getElementById("enter")


let massageInsList = [];
let massageSendNum = 0;
let allchatHistory;
let chatHistory;

function loadChatHistory() {
  let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
  
  if (storedChatHistoryJson) {
    allchatHistory = JSON.parse(storedChatHistoryJson);
    chatHistory = allchatHistory["first"];
    
    if (chatHistory) {
        
        chatHistory.forEach((message) => {
          const newMessage = document.createElement("div");
          newMessage.textContent = message["content"];
          
          if (message["role"] == "user") {
            newMessage.classList.add("chat_user_style");
          } else if (message["role"] == "assistant") {
            newMessage.classList.add("chat_GPT_style");
          } else {
            return;
          }
          chatbox.appendChild(newMessage);
        });
        chatbox.scrollTop = chatbox.scrollHeight;
    }
    
    
  } else {
      storedChatHistory = {};
      storedChatHistory["instanceCount"] = {};
      storedChatHistory["first"] = [];
      storedChatHistory["instanceCount"]["first"] = 0;
      
      localStorage.setItem("storedChatHistory", JSON.stringify(storedChatHistory));
  }
}

loadChatHistory();
// -------
socket.onopen = function(event) {
  console.log("Connection opened.", event);
};

socket.onclose = function(event) {
  console.log("Connection closed.", event);
};

socket.onmessage = function(event) {
  const jsonData = JSON.parse(event.data);
  if ( jsonData["chatHistory"] != null) {
    chatHistory = jsonData["chatHistory"];
  }
  message = jsonData["message"];
  messageSYS = jsonData["messageSYS"];
  messageID = jsonData["messageID"];
  state = jsonData["state"]
  console.log("Received message from server: ", event.data);
  if (messageSYS != null) {
      alert(messageSYS)
  }
  if (massageInsList[messageID]) {
      if (message == null) {
          message = "";
      }
      massageInsList[messageID].textContent += message;
      chatbox.appendChild(massageInsList[messageID]);
  } else {
      massageInsList[messageID] = document.createElement("div");
      massageInsList[messageID].classList.add("chat_GPT_style");
      massageInsList[messageID].textContent += message;
      chatbox.appendChild(massageInsList[messageID]);
  }
  chatbox.scrollTop = chatbox.scrollHeight;
  
  let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
  allchatHistory = JSON.parse(storedChatHistoryJson);

  allchatHistory["first"] = chatHistory;
  localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
}

// -------


function proscenario(){
  return;
}

// 检测用户输入并输出
function prossceSend(){
  const message = input.value.trim();
  const inputTemperature = inputTemp.value.trim();
  const inputToken = inputTkn.value.trim();
  const selected_scenario = inputSnr.value.trim();
  const Key = inputKey.value.trim();
  let inputmodel = "gpt-3.5-turbo";
  if (!Key) {
    alert("请输入密钥");
    return;
  }

  if (message) {
    const newMessage = document.createElement("div");
    newMessage.textContent = message;
    newMessage.classList.add("chat_user_style");
    chatbox.appendChild(newMessage);
    storedChatHistoryJson = localStorage.getItem("storedChatHistory");
    let allchatHistory = JSON.parse(storedChatHistoryJson);
    console.log(allchatHistory);
    allchatHistory["instanceCount"]["first"] += 1;
    massageSendStr = String(allchatHistory["instanceCount"]["first"]);
    localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
    
    chatHistory = allchatHistory["first"];
    
    
    // Send the message to the server
    socket.send(JSON.stringify({Key, selected_scenario,massageSendStr, chatHistory, message, inputTemperature, inputToken, inputmodel}));
    

    input.value = "";
    chatbox.scrollTop = chat.scrollHeight;
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