import os
from dotenv import load_dotenv
from agent import Agent, Tool
from colorama import init, Fore

# Initialize colorama for colored output
init()

def main():
    # Load environment variables
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.RED}Error: OPENAI_API_KEY not found in .env file{Fore.RESET}")
        return

    # Create agent instance
    agent = Agent()

    # Load previous conversation if exists
    memory_file = "conversation_history.json"
    agent.memory.load_from_file(memory_file)

    print(f"{Fore.GREEN}AI Agent initialized. Type 'exit' to quit.{Fore.RESET}")
    print(f"{Fore.CYAN}Available tools: get_time, calculate, cmd, python{Fore.RESET}")

    while True:
        try:
            user_input = input(f"{Fore.YELLOW}You: {Fore.RESET}")
            
            if user_input.lower() == 'exit':
                # Save conversation history before exiting
                agent.memory.save_to_file(memory_file)
                break

            response = agent.process_message(user_input)
            print(f"{Fore.GREEN}Agent: {Fore.RESET}{response}")

        except KeyboardInterrupt:
            # Save conversation history on interrupt
            agent.memory.save_to_file(memory_file)
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Fore.RESET}")

    print(f"{Fore.YELLOW}Goodbye!{Fore.RESET}")

if __name__ == "__main__":
    main()