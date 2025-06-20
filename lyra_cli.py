from lyra_agent import llm_respond_with_groq

print("Welcome to Lyra CLI! Type your message and press Enter. Type 'exit' or 'quit' to leave.")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
    response = llm_respond_with_groq(user_input)
    print(f"Lyra: {response['response']}") 