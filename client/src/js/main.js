const { invoke } = window.__TAURI__.tauri;

let apiUri = "http://localhost:58795"

async function sha256(password) {
  const msgUint8 = new TextEncoder().encode(password);                           
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);           
  const hashArray = Array.from(new Uint8Array(hashBuffer));                    
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); 
  return hashHex;
}

async function fetchToken() {
  const username = document.querySelector('input[type="text"]').value;
  const password = await sha256(document.querySelector('input[type="password"]').value);
  
  try {
      const response = await window.__TAURI__.http.fetch(`${apiUri}/access`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: window.__TAURI__.http.Body.json({ username, password }),
      });

      if (response.ok) {
        console.log(response);
          
          sessionStorage.setItem('token', response.data.session);
          window.location.href = 'app.html';
      } else {
          console.error('Authentication failed:', await response);
          window.location.href = 'index.html';
      }
  } catch (error) {
      console.error('Error:', error);
      window.location.href = 'index.html';
  }
}

document.querySelector('form').addEventListener('submit', (event) => {
  console.log("one more time!");
  event.preventDefault();
  fetchToken();
});

function checkSession() {
  const token = sessionStorage.getItem('token');
  if (!token) {
      window.location.href = 'index.html';
  }
}

if(window.location.pathname != '/index.html')
  checkSession();



let greetInputEl;
let greetMsgEl;

async function greet() {
  greetMsgEl.textContent = await invoke("greet", { name: greetInputEl.value });
}

window.addEventListener("DOMContentLoaded", () => {
  greetInputEl = document.querySelector("#greet-input");
  greetMsgEl = document.querySelector("#greet-msg");
  document.querySelector("#greet-form").addEventListener("submit", (e) => {
    e.preventDefault();
    greet();
  });
});

function randomcall() {
  console.error("porco dio")
}