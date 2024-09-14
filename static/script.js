document.addEventListener('DOMContentLoaded', function() {
    // Chatbot functionality
    const chatbotToggler = document.getElementById('chatbot-toggler');
    const chatbot = document.getElementById('chatbot');
    const closeChatbot = document.getElementById('close-chatbot');
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');

    // Toggle chatbot visibility
    chatbotToggler.addEventListener('click', function() {
        if (chatbot.style.display === 'none' || chatbot.style.display === '') {
            chatbot.style.display = 'flex'; // Show the chatbot
        } else {
            chatbot.style.display = 'none'; // Hide the chatbot
        }
    });

    // Close chatbot
    closeChatbot.addEventListener('click', function() {
        chatbot.style.display = 'none'; // Hide the chatbot
    });

    // Send message
    sendBtn.addEventListener('click', async function() {
        const message = userInput.value.trim(); // Get user input
        if (message) {
            // Create and append user's message to chat log
            const userMessage = document.createElement('li');
            userMessage.classList.add('outgoing');
            userMessage.textContent = message;
            chatLog.appendChild(userMessage);
            userInput.value = ''; // Clear input field

            // Scroll to the bottom after adding the user message
            chatLog.scrollTop = chatLog.scrollHeight;

            try {
                // Send user input to the Flask backend
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_question: message }), // Send the question
                });

                // Check if the response is OK
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.text(); // Parse response as text
                // Create and append bot's response to chat log
                const botMessage = document.createElement('li');
                botMessage.classList.add('incoming');
                botMessage.textContent = data; // Display the response from the backend
                chatLog.appendChild(botMessage);
                
                // Scroll to the bottom after adding the bot message
                chatLog.scrollTop = chatLog.scrollHeight;

            } catch (error) {
                console.error('Error:', error);
                // Handle error response from the server
                const errorMessage = document.createElement('li');
                errorMessage.classList.add('incoming');
                errorMessage.textContent = "Sorry, I couldn't process your request. Please try again.";
                chatLog.appendChild(errorMessage);
                
                // Scroll to the bottom after adding the error message
                chatLog.scrollTop = chatLog.scrollHeight;
            }
        }
    });

    // Allow pressing Enter to send the message
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendBtn.click(); // Trigger the send button click
            event.preventDefault(); // Prevent the default action (new line)
        }
    });
});
