from config import Config
from llama_interface import LLaMAInterface
from input_collector import InputCollector
from prompt_builder import PromptBuilder


def print_header():
    # Print welcome header
    print("\n" + Config.SEPARATOR)
    print("SPLENDOR GAME ADVISOR - MANUAL INPUT MODE")
    print(Config.SEPARATOR)
    print("\nGet strategic advice from your local LLaMA model!")
    print("Make sure your LLaMA is running before continuing.\n")


def main():
    # Main application loop
    print_header()
    
    # Get LLaMA configuration
    api_url, model = Config.get_api_settings()
    
    # Initialize components
    llama = LLaMAInterface(api_url, model)
    collector = InputCollector()
    builder = PromptBuilder()
    
    # Test connection
    print("\n" + Config.SEPARATOR)
    print("Testing LLaMA connection...")
    if not llama.test_connection():
        print("Cannot connect to LLaMA. Please check:")
        print("  1. Is Ollama/llama.cpp running?")
        print("  2. Is the model downloaded?")
        print("  3. Is the API URL correct?")
        return
    print("Connection successful!")
    
    # Main loop
    while True:
        try:
            # Collect game state
            game_state = collector.collect_full_game_state()
            
            # Build prompt
            prompt = builder.build_advisor_prompt(game_state)
            
            # Get advice from LLaMA
            print("\n" + Config.SEPARATOR)
            print("GENERATING ADVICE...")
            print(Config.SEPARATOR)
            
            advice = llama.generate(prompt)
            
            # Display results
            print("\n" + Config.SEPARATOR)
            print("LLAMA ADVISOR RECOMMENDATIONS:")
            print(Config.SEPARATOR)
            print(advice)
            print("\n" + Config.SEPARATOR)
            
            # Continue?
            again = input("\nAnalyze another game state? (y/n): ").lower()
            if again != 'y':
                print("\nThanks for using the Splendor Game Advisor!")
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting... Thanks for using the Splendor Game Advisor!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            continue


if __name__ == "__main__":
    main()