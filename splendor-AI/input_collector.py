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

# ============================================================================
# FILE: game_state.py
# ============================================================================
# Data structures for representing Splendor game state

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class Card:
    # Represents a Splendor card
    color: str
    level: int
    points: int
    cost: Dict[str, int] = field(default_factory=dict)
    
    def __str__(self):
        cost_str = ", ".join([f"{v} {k}" for k, v in self.cost.items()])
        return f"Level {self.level} {self.color} ({self.points} pts, costs: {cost_str})"


@dataclass
class Noble:
    # Represents a noble tile
    points: int
    requirements: Dict[str, int]
    
    def __str__(self):
        req_str = ", ".join([f"{v} {k}" for k, v in self.requirements.items()])
        return f"Noble worth {self.points} points (requires: {req_str})"


@dataclass
class GameState:
    # Complete game state
    gems: Dict[str, int]
    cards: List[Card]
    available_cards: List[Card]
    nobles: List[Noble]
    score: int
    opponent_score: int
    
    def get_card_summary(self) -> Dict[str, int]:
        # Get summary of owned cards by color
        summary = {}
        for card in self.cards:
            summary[card.color] = summary.get(card.color, 0) + 1
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        # Convert to dictionary format
        return {
            'gems': self.gems,
            'cards': [{'color': c.color, 'level': c.level, 'points': c.points} 
                     for c in self.cards],
            'available_cards': [{'color': c.color, 'level': c.level, 
                               'points': c.points, 'cost': c.cost} 
                              for c in self.available_cards],
            'nobles': [{'points': n.points, 'requirements': n.requirements} 
                      for n in self.nobles],
            'score': self.score,
            'opponent_score': self.opponent_score
        }

# ============================================================================
# FILE: llama_interface.py
# ============================================================================
# Interface for communicating with local LLaMA model

import requests
from typing import Optional
from config import Config


class LLaMAInterface:
    # Handles communication with LLaMA API
    
    def __init__(self, api_url: str, model: str):
        self.api_url = api_url
        self.model = model
        self.config = Config()
    
    def generate(self, prompt: str) -> Optional[str]:
        # Send prompt to LLaMA and get response
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.TEMPERATURE,
                "top_p": self.config.TOP_P,
                "max_tokens": self.config.MAX_TOKENS
            }
        }
        
        try:
            print(f"Connecting to LLaMA ({self.model})...")
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from model')
            
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to LLaMA. Is it running?"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try again."
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
    
    def test_connection(self) -> bool:
        # Test if LLaMA is accessible
        try:
            response = self.generate("Say 'OK' if you can read this.")
            return response is not None and "Error:" not in response
        except:
            return False

# ============================================================================
# FILE: input_collector.py
# ============================================================================
# Interactive system for collecting game state from user input

from typing import Dict, List
from config import Config
from game_state import Card, Noble, GameState


class InputCollector:
    # Collects game state through interactive prompts
    
    def __init__(self):
        self.config = Config()
    
    def _get_int_input(self, prompt: str, default: int = 0) -> int:
        # Helper to get integer input with validation
        while True:
            try:
                value = input(prompt)
                return int(value) if value else default
            except ValueError:
                print("Please enter a valid number.")
    
    def collect_gems(self) -> Dict[str, int]:
        # Collect player's gem tokens
        print("\n" + self.config.SEPARATOR)
        print("YOUR GEM TOKENS")
        print(self.config.SEPARATOR)
        
        gems = {}
        for gem in self.config.GEM_TYPES:
            gems[gem] = self._get_int_input(
                f"How many {gem.upper()} gems? "
            )
        return gems
    
    def collect_owned_cards(self) -> List[Card]:
        # Collect player's purchased cards
        print("\n" + self.config.SEPARATOR)
        print("YOUR PURCHASED CARDS")
        print(self.config.SEPARATOR)
        
        num_cards = self._get_int_input("How many cards do you own? ")
        cards = []
        
        for i in range(num_cards):
            print(f"\nCard {i+1}:")
            color = input("  Color (red/blue/green/white/black): ").lower()
            level = self._get_int_input("  Level (1/2/3): ", 1)
            points = self._get_int_input("  Points: ", 0)
            
            cards.append(Card(color=color, level=level, points=points))
        
        return cards
    
    def collect_available_cards(self) -> List[Card]:
        # Collect visible cards on the board
        print("\n" + self.config.SEPARATOR)
        print("AVAILABLE CARDS ON BOARD")
        print(self.config.SEPARATOR)
        print("(Enter cards you're considering buying)")
        
        num_cards = self._get_int_input("\nHow many available cards to analyze? ")
        cards = []
        
        for i in range(num_cards):
            print(f"\nAvailable Card {i+1}:")
            color = input("  Color: ").lower()
            level = self._get_int_input("  Level (1/2/3): ", 1)
            points = self._get_int_input("  Points: ", 0)
            
            print("  Cost (enter 0 if none):")
            cost = {}
            for gem in self.config.GEM_TYPES[:-1]:
                c = self._get_int_input(f"    {gem}: ", 0)
                if c > 0:
                    cost[gem] = c
            
            cards.append(Card(color=color, level=level, points=points, cost=cost))
        
        return cards
    
    def collect_nobles(self) -> List[Noble]:
        # Collect noble tiles
        print("\n" + self.config.SEPARATOR)
        print("NOBLE TILES")
        print(self.config.SEPARATOR)
        
        num_nobles = self._get_int_input("How many nobles are available? ")
        nobles = []
        
        for i in range(num_nobles):
            print(f"\nNoble {i+1}:")
            print("  Requirements (enter 0 if none):")
            requirements = {}
            for gem in self.config.GEM_TYPES[:-1]:
                r = self._get_int_input(f"    {gem} cards needed: ", 0)
                if r > 0:
                    requirements[gem] = r
            
            nobles.append(Noble(points=self.config.NOBLE_POINTS, requirements=requirements))
        
        return nobles
    
    def collect_scores(self) -> tuple:
        # Collect current scores
        print("\n" + self.config.SEPARATOR)
        print("SCORES")
        print(self.config.SEPARATOR)
        
        your_score = self._get_int_input("Your current score: ")
        opponent_score = self._get_int_input("Opponent's current score: ")
        return your_score, opponent_score
    
    def collect_full_game_state(self) -> GameState:
        # Collect complete game state
        print("\n" + self.config.SEPARATOR)
        print("SPLENDOR GAME STATE INPUT")
        print(self.config.SEPARATOR)
        print("Enter the current game state to get advice from LLaMA\n")
        
        gems = self.collect_gems()
        cards = self.collect_owned_cards()
        available_cards = self.collect_available_cards()
        nobles = self.collect_nobles()
        score, opponent_score = self.collect_scores()
        
        return GameState(
            gems=gems,
            cards=cards,
            available_cards=available_cards,
            nobles=nobles,
            score=score,
            opponent_score=opponent_score
        )
