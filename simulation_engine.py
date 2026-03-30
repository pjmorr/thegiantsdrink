# simulation_engine.py


class GameState:
    """Mutable state of a game session including position, inventory, and flags.

    Tracks the player's current room, collected items, and key progression
    flags (giant defeated, potion active, book read, door unlocked). Provides
    methods for movement, item interaction, combat, and room description.

    Attributes:
        current_room: Name of the room the player is currently in.
        inventory: List of Item objects the player is carrying.
        giant_defeated: Whether the giant has been defeated.
        potion_active: Whether the magic potion buff is active.
        book_knowledge: Whether the player has read the ancient book.
        door_unlocked: Whether the Victory Chamber door is unlocked.
    """

    def __init__(self):
        """Initialize a new game state in the Starting Room with empty inventory."""
        self.current_room = "Starting Room"
        self.inventory = []
        self.giant_defeated = False
        self.potion_active = False
        self.book_knowledge = False
        self.door_unlocked = False

    def move(self, direction, world_map):
        """Move the player in a given direction if the exit exists.

        direction (str): Cardinal direction (north, south, east, west, up, down).
        world_map (dict): Mapping of room names to Room objects.

        str: Description of the move result or error message.
        """
        room = world_map[self.current_room]
        if direction in room.exits:
            target_room = room.exits[direction]
            # Victory Chamber requires unlocked door
            if target_room == "Victory Chamber" and not self.door_unlocked:
                return "The iron door is locked. You need a key."
            self.current_room = target_room
            return f"You move to the {self.current_room}."
        return "You can't go that way."

    def take_item(self, item_name, world_map):
        """Pick up an item from the current room and add it to inventory.

        item_name (str): Name or partial name of the item to take (case-insensitive).
        world_map (dict): Mapping of room names to Room objects.

        str: Success message or error message if item not found.
        """
        for item in world_map[self.current_room].items:
            if item_name.lower() in item.name.lower():
                self.inventory.append(item)
                world_map[self.current_room].items.remove(item)
                return f"You take the {item.name}."
        return "There is no such item here."

    def use_item(self, item_name, difficulty=1.0):
        """Use an item from the player's inventory, triggering its effect.

        item_name (str): Name or partial name of the item to use (case-insensitive).
        difficulty (float, optional): Current game difficulty multiplier. Defaults to 1.0.

        str: Description of the item's effect or error message.
        """
        for item in self.inventory:
            if item_name.lower() in item.name.lower() and item.usable:
                if "potion" in item.name.lower():
                    self.inventory.remove(item)
                    self.potion_active = True
                    return "You drink the magic potion and feel a surge of strength!"
                elif "book" in item.name.lower():
                    self.book_knowledge = True
                    return (
                        "You read the ancient book and learn that the giant fears "
                        "his own drink turned against him. A crystal vial of his "
                        "draft may be hidden somewhere in the castle..."
                    )
                elif "key" in item.name.lower():
                    if self.current_room in ("Throne Antechamber", "Giant's Hall"):
                        self.door_unlocked = True
                        return "You use the key — the iron door clicks open!"
                    return "There is nothing to unlock here."
                elif "crystal vial" in item.name.lower():
                    if self.current_room == "Giant's Hall":
                        self.inventory.remove(item)
                        self.giant_defeated = True
                        return (
                            "You hurl the crystal vial at the giant. The luminous "
                            "liquid splashes across him and he shrieks — his own "
                            "strength turned against him! The giant crumbles to dust."
                        )
                    return "There is no one here to use this on."
                elif "shield" in item.name.lower():
                    return "You raise the silver shield. It might protect you in battle."
                elif "torch" in item.name.lower():
                    return "The torch flares brightly, pushing shadows to the walls."
                elif "helm" in item.name.lower():
                    return "You put on the iron helm. You feel tougher."
        return "You can't use that item or it's not in your inventory."

    def attack(self, target, difficulty=1.0):
        """Attack a target using equipped weapons, potentially defeating the giant.

        Implements three victory paths:
        - Aggressor: Sword + potion at high difficulty.
        - Strategist: Sword + book knowledge + potion.
        - Explorer: Crystal vial weapon (instant victory).

            target (str): Name of the target to attack (e.g., "giant").
            difficulty (float, optional): Current game difficulty multiplier. Defaults to 1.0.

            str: Combat result message or resource requirement message.
        """
        if self.current_room == "Giant's Hall" and "giant" in target.lower():
            has_sword = any("rusty sword" in item.name for item in self.inventory)

            if not has_sword:
                return "You try to attack the giant but fail without a weapon."

            # ── Aggressor path ──
            # High difficulty: giant requires potion before sword succeeds
            if difficulty > 1.2:
                if self.potion_active:
                    self.giant_defeated = True
                    return (
                        "Empowered by the potion, you strike the giant with the "
                        "rusty sword. The blow lands true — the giant falls!"
                    )
                return (
                    "You swing the rusty sword at the giant, but he is too "
                    "powerful. Perhaps a potion could give you the edge you need."
                )

            # ── Strategist path ──
            # Book knowledge + potion = guaranteed success at any difficulty
            if self.book_knowledge and self.potion_active:
                self.giant_defeated = True
                return (
                    "Armed with knowledge from the ancient book and empowered by "
                    "the magic potion, you strike the giant's weakness. He topples "
                    "like a felled oak!"
                )

            # Low difficulty: direct attack succeeds without potion
            if difficulty < 0.9:
                self.giant_defeated = True
                return "The giant is sluggish and slow. You strike with the rusty sword and defeat him with ease!"

            # Normal difficulty: sword alone works
            self.giant_defeated = True
            return "You attack the giant with the rusty sword and defeat him!"

        return "There is nothing to attack here."

    def get_current_description(self, world_map):
        """Get a full description of the current room including items and exits.

        world_map (dict): Mapping of room names to Room objects.

        str: Formatted room description with items visible and available exits.
        """
        room = world_map[self.current_room]
        description = room.description
        if room.items:
            description += " You see: " + ", ".join([item.name for item in room.items])
        exits = ", ".join(room.exits.keys())
        description += f"\nExits: {exits}"
        return description
