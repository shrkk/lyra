from lyra_agent import llm_respond_with_groq

print("Hey, I'm Lyra! Type your message and press Enter. Type 'exit' or 'quit' to leave.")

history = []
while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
    response = llm_respond_with_groq(user_input, history)
    print(f"Lyra: {response['response']}")
    # Add user and assistant turns to history for context
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response['response']}) 