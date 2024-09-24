import os
import ollama

def chat_with_bot(user_question):
    modified_question = user_question + " in short"
    context=f"this is a chatbot model in which we are using ollama so only response for the question asked do not mention the ollama detection and this is a healthcare web-app give accurate solution.user: {modified_question}"

    stream = ollama.chat(
        model='llama3',
        messages=[{
            'role': 'user',
            'content': context,
        }],
        stream=True,
    )
    
    response = ""
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            response += chunk['message']['content']
        else:
            print("Chunk received without expected structure:", chunk)  # Debugging line
    
    if not response:
        print("No response received from the chatbot.")  # Debugging line
    
    return response

def main(user_question):
    try:
        while True:
            if user_question.lower() == 'exit' or user_question.lower == 'bye':
                print("Goodbye...")
                break
            
            # Send the user's question to the chatbot
            response = chat_with_bot(user_question)
            return response
    
    except Exception as e:
        print(f"Error: {e}")

