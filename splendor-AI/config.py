class Config:
    # LLaMA API Settings
    DEFAULT_API_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "llama2"
    
    # LLaMA Generation Settings
    TEMPERATURE = 0.7
    TOP_P = 0.9
    MAX_TOKENS = 500
    REQUEST_TIMEOUT = 60
    
    # Game Constants
    GEM_TYPES = ['red', 'blue', 'green', 'white', 'black', 'gold']
    CARD_LEVELS = [1, 2, 3]
    NOBLE_POINTS = 3
    
    # Display Settings
    SEPARATOR = "=" * 60
    
    @classmethod
    def get_api_settings(cls):
        # Get API configuration from user or use defaults
        print("\n" + cls.SEPARATOR)
        print("LLAMA CONFIGURATION")
        print(cls.SEPARATOR)
        print(f"Default: Ollama at {cls.DEFAULT_API_URL}")
        print()
        
        use_custom = input("Use custom LLaMA endpoint? (y/n, default=n): ").lower()
        
        if use_custom == 'y':
            api_url = input("Enter LLaMA API URL: ")
            model = input("Enter model name (e.g., llama2, llama3, mistral): ")
        else:
            api_url = cls.DEFAULT_API_URL
            model = input(f"Enter model name (default={cls.DEFAULT_MODEL}): ") or cls.DEFAULT_MODEL
        
        return api_url, model
