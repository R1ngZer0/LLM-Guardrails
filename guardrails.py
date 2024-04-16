import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Initialize the OpenAI client
load_dotenv() # Load env variables from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

conversation_history = []

def update_conversation_history(role, message):
    global conversation_history
    conversation_history.append({"role": role, "content": message})

def load_functions_list():
    # Load functions list from a text file 
    try:
        with open('functions.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Functions list file not found.")
        return ""
    
def load_criteria():
    # Load functions list from a text file 
    try:
        with open('criteria.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Functions list file not found.")
        return ""


# Guardrail Agent ###############################################################################
def validate_prompt(user_message, functions_list):
    criteria = load_criteria()

    system_prompt = f"You area guardrail assistant with the task of making sure that all user prompts meet the proper criteria before being allowed to pass through to the LLM. You will be asked to evaluate a user prompt. Based on the evaluation criteria and your analysis, look through the available functions and contents and tell me which one can best provide me what I need based on my question. Reply with the name of the function and nothing else. Do not include the parentheis. Evaluation Criteria: {criteria}\n\nAvailable Functions: {functions_list}\n\nReply with the name of the function and nothing else. Do not include the parentheis."
    prompt = f"Evaluate the following prompt: {user_message}"

    # Send the request to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500,
        )
    except Exception as e:
        print("An error occurred while connecting to the OpenAI API:", e)
        return f"An error occurred while connecting to the OpenAI API: {e}"

    # Extract the answer
    answer = response.choices[0].message.content.strip()
    print(f"Function: {answer}")
    return answer


# Chat Agent ####################################################################################
def general_message():
    # Send the request to OpenAI
    #print(conversation_history)
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation_history,
            temperature=0.7,
        )
    except Exception as e:
        #print("An error occurred while connecting to the OpenAI API:", e)
        return f"An error occurred while connecting to the OpenAI API: {e}"

    # Extract the answer
    answer = response.choices[0].message.content.strip()
    update_conversation_history("assistant", answer)
    #print(f"{answer}\n")
    return answer

def invalid_prompt():
    answer = "I'm unable to do that."
    update_conversation_history("assistant", answer)
    return answer


###############################################################################################
###############################################################################################

def start(user_message):
    update_conversation_history("user", user_message)

    # Load functions list from functions.txt
    functions_list = load_functions_list()

    function_mapping = {
        "general_message": general_message,
        "invalid_prompt": invalid_prompt,
    }

    # Check if functions list is empty
    if not functions_list:
        print("Functions list is empty. Please ensure functions.txt is populated.")

    function_name_str = validate_prompt(user_message, functions_list)
    function_to_call = function_mapping.get(function_name_str)

    if function_to_call:
        if function_to_call == general_message:
            result = general_message()
            return result
        if function_to_call == invalid_prompt:
            result = invalid_prompt()
            return result
        else:
            result = function_to_call()
            return result
    else:
        return f"Error: {function_name_str}"
