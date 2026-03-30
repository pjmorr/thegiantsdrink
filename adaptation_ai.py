# adaptation_ai.py


class AdaptationAI:
    """Dynamic difficulty and world adaptation based on player behavior.

    Adjusts the difficulty multiplier and modifies the world map in response
    to the player's detected play style (aggressive, exploratory, strategic).

    Attributes:
        difficulty_multiplier: Current difficulty scaling factor.
        player_summary: Textual description of the player's style.
    """

    def __init__(self):
        """Initialize AdaptationAI with default difficulty and no world modifications."""
        self.difficulty_multiplier = 1.0
        self.player_summary = ""
        self._corridor_blocked = False
        self._hidden_passage_revealed = False

    def adjust_difficulty(self, profile, profile_summary=""):
        """Adjust game difficulty based on the player's detected behavior profile.

        profile (dict): Player profile with 'exploration', 'aggression', 'strategy' keys.
        profile_summary (str, optional): Textual description of player style. Defaults to ''.

        """
        self.player_summary = profile_summary

        if profile["aggression"] > 5:
            self.difficulty_multiplier = 1.5
        elif profile["strategy"] > 5:
            self.difficulty_multiplier = 0.8
        else:
            self.difficulty_multiplier = 1.0

    def get_difficulty(self):
        """Get the current difficulty multiplier.

        float: Current difficulty multiplier (typically 0.8, 1.0, or 1.5).
        """
        return self.difficulty_multiplier

    def adapt_world(self, world_map, profile, profile_summary=""):
        """Modify the world dynamically based on detected player behavior.

        Aggressive players find the Corridor blocked, forcing detour through Dungeon.
        Explorers discover a hidden passage from Library to Hidden Study.

            world_map (dict): Mapping of room names to Room objects (modified in-place).
            profile (dict): Player profile with 'exploration', 'aggression', 'strategy' keys.
            profile_summary (str, optional): Textual description of player style. Defaults to ''.

        """
        # Aggressive player: block the direct Corridor -> Great Staircase path
        if profile["aggression"] > 3 and not self._corridor_blocked:
            if "north" in world_map["Corridor"].exits:
                del world_map["Corridor"].exits["north"]
                # Open dungeon access from Starting Room
                world_map["Starting Room"].exits["down"] = "Dungeon"
                world_map["Corridor"].description = (
                    "A long passage stretches before you, its vaulted ceiling lost in "
                    "darkness. Faded tapestries line the walls. The northern archway has "
                    "collapsed — a massive beam blocks the way. You'll need another route "
                    "upstairs. Doors branch east and west."
                )
                self._corridor_blocked = True

        # Explorer player: reveal hidden passage in Library
        if profile["exploration"] > 4 and not self._hidden_passage_revealed:
            world_map["Library"].exits["west"] = "Hidden Study"
            world_map["Hidden Study"].exits["east"] = "Library"
            world_map["Library"].description = (
                "Shelves of ancient books climb to a ceiling you cannot see. Your keen "
                "explorer's eye spots something others would miss — one bookcase sits "
                "slightly proud of the wall. Behind it, a hidden passage leads west "
                "into shadow. The ancient book still lies open on its stand."
            )
            self._hidden_passage_revealed = True
