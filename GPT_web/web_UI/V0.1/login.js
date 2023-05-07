const socket = new WebSocket("ws://192.168.1.105:3000");

const messageElement = document.getElementById("message");
const loginForm = document.getElementById("login-form");



loginForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  socket.send(JSON.stringify({ username, password }));
  
  

});




socket.addEventListener("message", (event) => {

  const response = JSON.parse(event.data);
  if (response.status === 'success') {
    setCookie('token', response.token, 1);
    window.location.href = "/chat.html"; // Redirect to chat page after successful login
    
  } else {
    
    messageElement.innerHTML = "Login failed!";
  }


});

function setCookie(name, value, days) {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}