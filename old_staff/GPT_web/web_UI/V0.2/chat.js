const socket = new WebSocket("ws://47.74.90.86:8080");
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const inputTemp = document.getElementById("inputTemperature");
const inputMod = document.getElementById("inputModel");
const inputTkn = document.getElementById("inputToken");
const inputSnr = document.getElementById("inputSnr");
const inputKey = document.getElementById("inputKey");
const selectElement = document.getElementById('mySelect');

let massageInsList = [];
let massageSendNum = 0;

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
          chat.appendChild(newMessage);
        });
        chat.scrollTop = chat.scrollHeight;
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





socket.onopen = function(event) {
  console.log("Connection opened.", event);
};

socket.onclose = function(event) {
  console.log("Connection closed.", event);
};





// socket.onmessage = function(event) {
//   console.log("Received message from server: ", event.data);
//   const newMessage = document.createElement("div");
  
//   //const jsonData = JSON.parse(event.data);
//   //chatHistory = jsonData["chatHistory"];
//   //message = jsonData["message"];
//   newMessage.classList.add("chat_GPT_style");
//   newMessage.textContent = event.data;
//   chat.appendChild(newMessage);
//   chat.scrollTop = chat.scrollHeight;
  
//   let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
//   allchatHistory = JSON.parse(storedChatHistoryJson);
  
//   allchatHistory["first"] = chatHistory;
//   localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
  //loadChatHistory("first");
// };

function stander(){
    socket.onmessage = function(event) {
  console.log("Received message from server: ", event.data);
  const newMessage = document.createElement("div");
  
  const jsonData = JSON.parse(event.data);
  if ( jsonData["chatHistory"] != null) {
    chatHistory = jsonData["chatHistory"];
  }
  message = jsonData["message"];
  newMessage.classList.add("chat_GPT_style");
  newMessage.textContent = message;
  chat.appendChild(newMessage);
  chat.scrollTop = chat.scrollHeight;
  
  let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
  allchatHistory = JSON.parse(storedChatHistoryJson);
  
  allchatHistory["first"] = chatHistory;
  localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
  //loadChatHistory("first");
};
}

function asynchronous(){
    let currentMessage = "";
    socket.onmessage = function(event) {
    const jsonData = JSON.parse(event.data);
    chatHistory = jsonData["chatHistory"];
    message = jsonData["message"];
    
    console.log("Received message from server: ", event.data);
    const newMessage = document.createElement("div");
    newMessage.classList.add("chat_GPT_style");
    chat.appendChild(newMessage);
    currentMessage += event.data;
    newMessage.textContent = currentMessage;
      socket.onmessage = function(event) {
      console.log("Received message from server: ", event.data);
      if (event.data !== '\n') {
    // 如果收到的字符不是换行符，将它添加到 currentMessage
        currentMessage += event.data;
        newMessage.textContent = currentMessage;
      } else {
    // 如果收到换行符，将拼接好的字符串添加到 chat 元素中
        chat.scrollTop = chat.scrollHeight;

    // 清空 currentMessage 以便存储新的字符串
        currentMessage = "";
  }}
};
}

socket.onmessage = function(event) {
    const jsonData = JSON.parse(event.data);
    chatHistory = jsonData["chatHistory"];
    message = jsonData["message"];
    state = jsonData["state"];
    messageID = jsonData["messageID"];
    console.log("Received message from server: ", event.data);
    if (massageInsList[messageID]) {
        if (message == null) {
            message = "";
        }
        massageInsList[messageID].textContent += message;
        chat.appendChild(massageInsList[messageID]);
    } else {
        massageInsList[messageID] = document.createElement("div");
        massageInsList[messageID].classList.add("chat_GPT_style");
        massageInsList[messageID].textContent += message;
        chat.appendChild(massageInsList[messageID]);
    }
    chat.scrollTop = chat.scrollHeight;
    
    let storedChatHistoryJson = localStorage.getItem("storedChatHistory");
    allchatHistory = JSON.parse(storedChatHistoryJson);
  
    allchatHistory["first"] = chatHistory;
    localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
}



input.addEventListener("keydown", function(event) {
    
  
  if (event.key === "Enter") {
    const message = input.value.trim();
    const inputTemperature = inputTemp.value.trim();
    const inputModel = inputMod.value.trim();
    const inputToken = inputTkn.value.trim();
    const selected_scenario = inputSnr.value.trim();
    const Key = inputKey.value.trim();
    
    if (!Key) {
        alert("请输入密钥");
        return;
      }

    if (message) {
      const newMessage = document.createElement("div");
      newMessage.textContent = message;
      newMessage.classList.add("chat_user_style");
      chat.appendChild(newMessage);
      storedChatHistoryJson = localStorage.getItem("storedChatHistory");
      let allchatHistory = JSON.parse(storedChatHistoryJson);
      console.log(allchatHistory);
      allchatHistory["instanceCount"]["first"] += 1;
      massageSendStr = String(allchatHistory["instanceCount"]["first"]);
      localStorage.setItem("storedChatHistory", JSON.stringify(allchatHistory));
      
      chatHistory = allchatHistory["first"];
      
      
      // Send the message to the server
      socket.send(JSON.stringify({Key, selected_scenario,massageSendStr, chatHistory, message, inputTemperature, inputModel, inputToken}));
      

      input.value = "";
      chat.scrollTop = chat.scrollHeight;
    }
  }
});