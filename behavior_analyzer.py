# behavior_analyzer.py
import time


class BehaviorAnalyzer:
    """Tracks and categorizes player actions to build a behavior profile.

    Records each action the player takes and maintains running counts for
    exploration, aggression, and strategy categories. Provides ratio analysis
    and plain-English summaries of the player's dominant play style.

    Attributes:
        profile: Dict with 'exploration', 'aggression', 'strategy' counts.
        action_history: Ordered list of all recorded action strings.
        read_book: Whether the player has read the ancient book.
    """

    def __init__(self):
        """Initialize BehaviorAnalyzer with zeroed profile and empty history."""
        self.profile = {
            "exploration": 0,
            "aggression": 0,
            "strategy": 0,
        }
        self.action_history = []
        self.action_timestamps = []
        self.first_action = None
        self.read_book = False

    def update_profile(self, action):
        """Record a player action and update the behavior profile accordingly.

        action (str): Action type to record (move, take, use, attack, check, etc.).

        """
        now = time.time()
        self.action_history.append(action)
        self.action_timestamps.append(now)

        if self.first_action is None:
            self.first_action = action

        if action == "move":
            self.profile["exploration"] += 1
        elif action == "attack":
            self.profile["aggression"] += 1
        elif action in ("use", "take", "check"):
            self.profile["strategy"] += 1

    def mark_book_read(self):
        """Mark that the player has read the ancient book."""
        self.read_book = True

    def get_profile(self):
        """Retrieve the current player behavior profile.

        dict: Profile with keys 'exploration', 'aggression', 'strategy' and their counts.
        """
        return self.profile

    def get_action_ratios(self):
        """Calculate the proportional breakdown of player actions (exploration, attack, use).

        dict: Ratios with keys 'explore', 'attack', 'use' (values 0.0-1.0).
        """
        total = len(self.action_history)
        if total == 0:
            return {"explore": 0.0, "attack": 0.0, "use": 0.0}
        explore_count = self.action_history.count("move")
        attack_count = self.action_history.count("attack")
        use_count = self.action_history.count("use")
        return {
            "explore": explore_count / total,
            "attack": attack_count / total,
            "use": use_count / total,
        }

    def read_book_before_attack(self):
        """Check if the player read the book before their first attack.

        bool: True if book was read before first attack, False otherwise.
        """
        if not self.read_book:
            return False
        book_index = None
        attack_index = None
        for i, action in enumerate(self.action_history):
            if action == "use" and book_index is None:
                book_index = i
            if action == "attack" and attack_index is None:
                attack_index = i
        if book_index is not None and attack_index is not None:
            return book_index < attack_index
        return book_index is not None

    def get_profile_summary(self):
        """Return a plain English description of the player's dominant play style.

        str: One-sentence summary (e.g., "aggressive fighter who acts before thinking").
        """
        ratios = self.get_action_ratios()
        total = len(self.action_history)

        if total == 0:
            return "new adventurer with no actions yet"

        prepared = self.read_book_before_attack()

        # Determine dominant style
        if ratios["attack"] > 0.4:
            style = "aggressive fighter"
        elif ratios["explore"] > 0.5:
            style = "cautious explorer"
        elif ratios["use"] > 0.3:
            style = "resourceful strategist"
        else:
            style = "balanced adventurer"

        if prepared:
            style += " who prepares before acting"
        elif ratios["attack"] > 0.3 and not prepared:
            style += " who acts before thinking"

        return style
