// Function to confirm appointment booking
function confirmAppointment(event) {
    event.preventDefault(); // Prevent the form from submitting immediately

    // Get the values from the appointment form
    const name = document.getElementById("name").value;
    const date = document.getElementById("appointment_date").value;
    const time = document.getElementById("appointment_time").value;
    const consultation = document.getElementById("consultation").value;

    // Create a confirmation message
    const confirmationMessage = `Are you sure you want to book this appointment?\n\n` +
        `Name: ${name}\n` +
        `Date: ${date}\n` +
        `Time: ${time}\n` +
        `Consultation with: ${consultation}`;

    // Show confirmation dialog
    if (confirm(confirmationMessage)) {
        document.getElementById("appointmentForm").submit(); // Submit the form if confirmed
    }
}

// Function to handle chatbot functionality
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

            // Disable the send button and show a loading indicator
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';

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
            } finally {
                // Re-enable the send button and restore the original text
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
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

// Attach the confirmAppointment function to the appointment form's submit event
document.addEventListener("DOMContentLoaded", function() {
    const appointmentForm = document.getElementById("appointmentForm");
    if (appointmentForm) {
        appointmentForm.addEventListener("submit", confirmAppointment);
    }
});

function confirmLogout(event) {
    event.preventDefault(); // Prevent the default link behavior
    const confirmation = confirm("Are you sure you want to log out?");
    if (confirmation) {
        window.location.href = "/logout"; // Redirect to logout route
    }
}
