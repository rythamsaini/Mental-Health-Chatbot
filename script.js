function sendMessage() {
    const userInput = document.getElementById('user_input');
    const chatbox = document.getElementById('chatbox');
    const message = userInput.value.trim();
    if (!message) return;
    chatbox.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
    userInput.value = '';
    fetch('/get_response', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        chatbox.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
    }).catch(err => {
        chatbox.innerHTML += `<div><strong>Bot:</strong> Sorry, I'm having trouble responding right now.</div>`;
    });
}

document.getElementById('user_input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});

document.getElementById('theme-toggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-theme');
});
