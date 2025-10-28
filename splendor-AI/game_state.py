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