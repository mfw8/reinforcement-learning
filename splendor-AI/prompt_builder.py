from game_state import GameState


class PromptBuilder:
    # Formats game state into effective prompts for LLaMA
    
    @staticmethod
    def build_advisor_prompt(game_state: GameState) -> str:
        # Build a comprehensive prompt for game advice
        
        prompt = "You are an expert Splendor board game strategist. Analyze the current game state and provide tactical advice to the player.\n\nCURRENT GAME STATE:\n\nPlayer Resources:\n"
        
        # Add gem resources
        for gem_type, count in game_state.gems.items():
            prompt += f"  - {gem_type}: {count}\n"
        
        # Add owned cards summary
        prompt += f"\nPlayer Cards ({len(game_state.cards)} total):\n"
        card_summary = game_state.get_card_summary()
        for color, count in card_summary.items():
            prompt += f"  - {count}x {color} cards\n"
        
        # Add available cards
        prompt += "\nAvailable Cards on Board:\n"
        for i, card in enumerate(game_state.available_cards, 1):
            prompt += f"  Card {i}: Level {card.level} {card.color}\n"
            if card.cost:
                cost_str = ", ".join([f"{v} {k}" for k, v in card.cost.items()])
                prompt += f"    Cost: {cost_str}\n"
            prompt += f"    Points: {card.points}\n"
        
        # Add nobles
        prompt += "\nNobles Available:\n"
        for i, noble in enumerate(game_state.nobles, 1):
            prompt += f"  Noble {i}: Worth {noble.points} points\n"
            if noble.requirements:
                req_str = ", ".join([f"{v} {k}" for k, v in noble.requirements.items()])
                prompt += f"    Requires: {req_str}\n"
        
        # Add scores
        prompt += f"\nCurrent Score: {game_state.score}\n"
        prompt += f"Opponent Score: {game_state.opponent_score}\n"
        
        # Add instructions
        prompt += "\nBased on this game state, provide:\n1. The best move to make right now (which card to buy or gems to take)\n2. Short-term strategy (next 2-3 moves)\n3. Long-term strategy considerations\n4. Any warnings about opponent threats\n\nKeep your advice concise and actionable."
        
        return prompt
