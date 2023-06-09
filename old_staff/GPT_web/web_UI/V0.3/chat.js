const socket = new WebSocket("wss://www.jackymo.cn:14569");
const inputTemp = document.getElementById("inputTemperature");
const inputTkn = document.getElementById("inputToken");
const inputSnr = document.getElementById("inputSnr");
// const inputSnrCus = document.getElementById("inputSnrCus");
const inputKey = document.getElementById("inputKey");
// const selectElement = document.getElementById('mySelect');
const chatbox = document.getElementById("chatbox");
var input = document.getElementById("input");
var Customersennario = document.getElementById("Customersennario");
var token_remainELE = document.getElementById("token_remain");
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

socket.onerror = function(event) {
  console.error("WebSocket error message:", event.message);
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
  token_remain = jsonData["usage"]
  console.log("Received message from server: ", event.data);
  if (messageSYS != null) {
      alert(messageSYS)
  }
  if (token_remain != null){
    token_remainELE.value = token_remain;
  }
  if (massageInsList[messageID]) {
      if (message == null) {
          message = "";
      }
      message = escapeHtml(message.replace(/\n/g, "<br/>").replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;"));
      massageInsList[messageID].innerHTML += message;
      chatbox.appendChild(massageInsList[messageID]);
  } else {
      massageInsList[messageID] = document.createElement("div");
      massageInsList[messageID].classList.add("chat_GPT_style");
      massageInsList[messageID].innerHTML += message;
      chatbox.appendChild(massageInsList[messageID]);
  }
  chatbox.scrollTop = chatbox.scrollHeight;
  
  let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
  allchatHistory = JSON.parse(storedChatHistoryJson);

  allchatHistory["first"] = chatHistory;
  localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
}

// -------
function escapeHtml(html) {
  var text = document.createTextNode(html);
  var p = document.createElement('p');
  p.appendChild(text);
  return p.innerHTML;
}

function proscenario(selected){
  if (selected == "assistant") {
    return "you are a helpful assistant";
  }
  if (selected == "Customer") {
    return Customersennario.value.trim();
  }
}

// 检测用户输入并输出
function prossceSend(){
  const message = input.value.trim();
  const inputTemperature = inputTemp.value.trim();
  const inputToken = inputTkn.value.trim();
  const selected_scenario_from_user = inputSnr.value.trim();
  const Key = inputKey.value.trim();
  let inputmodel = "gpt-3.5-turbo";
  if (!Key) {
    alert("请输入密钥");
    return;
  }
  selected_scenario = proscenario(selected_scenario_from_user);
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
    chatbox.scrollTop = chatbox.scrollHeight;
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