# main.py
from adaptation_ai import AdaptationAI
from behavior_analyzer import BehaviorAnalyzer
from command_parser import parse_command
from content_generator import ContentGenerator
from game_world import world_map
from simulation_engine import GameState

HELP_TEXT = """Available commands:
  LOOK          - Look around the current room
  GO <direction> - Move north, south, east, or west
  TAKE <item>   - Pick up an item
  USE <item>    - Use an item from your inventory
  ATTACK <target> - Attack something
  INVENTORY     - Check your inventory
  HELP          - Show this help message
  QUIT / EXIT   - Leave the game"""


def main():
    """Run the main game loop for The Giant's Drink text adventure.

    Initializes GameState, behavior analyzer, adaptation AI, and content generator.
    Processes player commands until the giant is defeated. Continuously adapts
    difficulty and world state based on player profile.


    """
    game_state = GameState()
    behavior_analyzer = BehaviorAnalyzer()
    adaptation_ai = AdaptationAI()
    content_gen = ContentGenerator()

    print("Welcome to The Giant's Drink!")
    print("Type HELP for a list of commands.\n")
    print(game_state.get_current_description(world_map))

    while not game_state.giant_defeated:
        command = input("\n> ").strip()
        if not command:
            continue

        action, target = parse_command(command)

        if action == "move" and target:
            result = game_state.move(target, world_map)
            behavior_analyzer.update_profile("move")
        elif action == "take" and target:
            result = game_state.take_item(target, world_map)
            behavior_analyzer.update_profile("take")
        elif action == "use" and target:
            difficulty = adaptation_ai.get_difficulty()
            result = game_state.use_item(target, difficulty)
            behavior_analyzer.update_profile("use")
            if "book" in target.lower():
                behavior_analyzer.mark_book_read()
        elif action == "attack" and target:
            difficulty = adaptation_ai.get_difficulty()
            result = game_state.attack(target, difficulty)
            behavior_analyzer.update_profile("attack")
        elif action == "check" and target == "inventory":
            result = (
                "Inventory: " + ", ".join([item.name for item in game_state.inventory])
                if game_state.inventory
                else "Your inventory is empty."
            )
            behavior_analyzer.update_profile("check")
        elif action == "look":
            result = game_state.get_current_description(world_map)
        elif action == "help":
            result = HELP_TEXT
        elif action == "quit":
            print("Thanks for playing The Giant's Drink!")
            return
        else:
            result = "I do not understand that command. Type HELP for a list of commands."

        print(result)

        if action in ("move", "take", "use", "attack"):
            room = world_map[game_state.current_room]
            profile_summary = behavior_analyzer.get_profile_summary()
            try:
                desc = content_gen.generate_description(
                    room.name,
                    behavior_analyzer.get_profile(),
                    description=room.description,
                    items=[item.name for item in room.items],
                    profile_summary=profile_summary,
                )
            except Exception:
                desc = game_state.get_current_description(world_map)
            else:
                if room.items:
                    desc += " You see: " + ", ".join(item.name for item in room.items)
                desc += f"\nExits: {', '.join(room.exits.keys())}"
            print(desc)

        profile = behavior_analyzer.get_profile()
        profile_summary = behavior_analyzer.get_profile_summary()
        adaptation_ai.adjust_difficulty(profile, profile_summary)
        adaptation_ai.adapt_world(world_map, profile, profile_summary)

    print("\nCongratulations! You have defeated the giant and won the game!")


if __name__ == "__main__":
    main()
