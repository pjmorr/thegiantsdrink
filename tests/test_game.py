# tests/test_game.py
import copy
import json
from unittest.mock import MagicMock, patch

import pytest

from adaptation_ai import AdaptationAI
from behavior_analyzer import BehaviorAnalyzer
from command_parser import command_cache, parse_command
from content_generator import ContentGenerator
from game_world import world_map
from simulation_engine import GameState


@pytest.fixture
def game():
    return GameState()


@pytest.fixture
def wmap():
    """Deep-copy the world map so tests don't mutate shared state."""
    return copy.deepcopy(world_map)


# ── Movement ─────────────────────────────────────────────────────────


class TestMovement:
    def test_move_north_from_start(self, game, wmap):
        result = game.move("north", wmap)
        assert game.current_room == "Corridor"
        assert "Corridor" in result

    def test_move_invalid_direction(self, game, wmap):
        result = game.move("west", wmap)
        assert game.current_room == "Starting Room"
        assert "can't" in result.lower()

    def test_move_through_multiple_rooms(self, game, wmap):
        game.move("north", wmap)  # -> Corridor
        game.move("east", wmap)  # -> Treasure Room
        assert game.current_room == "Treasure Room"
        game.move("west", wmap)  # -> Corridor
        assert game.current_room == "Corridor"

    def test_move_to_locked_victory_chamber(self, game, wmap):
        game.current_room = "Throne Antechamber"
        result = game.move("north", wmap)
        assert game.current_room == "Throne Antechamber"
        assert "locked" in result.lower()

    def test_move_to_victory_chamber_when_unlocked(self, game, wmap):
        game.current_room = "Throne Antechamber"
        game.door_unlocked = True
        game.move("north", wmap)
        assert game.current_room == "Victory Chamber"


# ── Inventory ────────────────────────────────────────────────────────


class TestInventory:
    def test_take_item(self, game, wmap):
        result = game.take_item("rusty sword", wmap)
        assert "rusty sword" in result.lower()
        assert len(game.inventory) == 1
        assert game.inventory[0].name == "rusty sword"

    def test_take_nonexistent_item(self, game, wmap):
        result = game.take_item("golden axe", wmap)
        assert "no such item" in result.lower()
        assert len(game.inventory) == 0

    def test_item_removed_from_room_after_take(self, game, wmap):
        game.take_item("rusty sword", wmap)
        assert len(wmap["Starting Room"].items) == 0

    def test_take_item_in_treasure_room(self, game, wmap):
        game.current_room = "Treasure Room"
        result = game.take_item("magic potion", wmap)
        assert "magic potion" in result.lower()
        assert len(game.inventory) == 1


# ── Item Use ─────────────────────────────────────────────────────────


class TestItemUse:
    def test_use_potion(self, game, wmap):
        game.current_room = "Treasure Room"
        game.take_item("magic potion", wmap)
        game.use_item("potion")
        assert game.potion_active is True
        assert len(game.inventory) == 0

    def test_use_book(self, game, wmap):
        game.current_room = "Library"
        game.take_item("ancient book", wmap)
        game.use_item("book")
        assert game.book_knowledge is True

    def test_use_key_in_antechamber(self, game, wmap):
        game.current_room = "Giant's Hall"
        game.take_item("key", wmap)
        game.current_room = "Throne Antechamber"
        game.use_item("key")
        assert game.door_unlocked is True

    def test_use_key_wrong_room(self, game, wmap):
        game.current_room = "Giant's Hall"
        game.take_item("key", wmap)
        game.current_room = "Library"
        game.use_item("key")
        assert game.door_unlocked is False

    def test_use_nonexistent_item(self, game, wmap):
        result = game.use_item("banana")
        assert "can't use" in result.lower()


# ── Combat ───────────────────────────────────────────────────────────


class TestCombat:
    def test_attack_giant_with_sword_normal_difficulty(self, game, wmap):
        game.take_item("rusty sword", wmap)
        game.current_room = "Giant's Hall"
        game.attack("giant", difficulty=1.0)
        assert game.giant_defeated is True

    def test_attack_giant_without_sword(self, game, wmap):
        game.current_room = "Giant's Hall"
        result = game.attack("giant", difficulty=1.0)
        assert game.giant_defeated is False
        assert "fail" in result.lower()

    def test_attack_giant_high_difficulty_no_potion(self, game, wmap):
        game.take_item("rusty sword", wmap)
        game.current_room = "Giant's Hall"
        result = game.attack("giant", difficulty=1.5)
        assert game.giant_defeated is False
        assert "potion" in result.lower()

    def test_attack_giant_high_difficulty_with_potion(self, game, wmap):
        game.take_item("rusty sword", wmap)
        game.current_room = "Giant's Hall"
        game.potion_active = True
        game.attack("giant", difficulty=1.5)
        assert game.giant_defeated is True

    def test_attack_giant_low_difficulty(self, game, wmap):
        game.take_item("rusty sword", wmap)
        game.current_room = "Giant's Hall"
        game.attack("giant", difficulty=0.5)
        assert game.giant_defeated is True

    def test_attack_nothing(self, game, wmap):
        result = game.attack("giant", difficulty=1.0)
        assert "nothing to attack" in result.lower()

    def test_crystal_vial_defeats_giant(self, game, wmap):
        game.current_room = "Hidden Study"
        game.take_item("crystal vial", wmap)
        game.current_room = "Giant's Hall"
        game.use_item("crystal vial")
        assert game.giant_defeated is True

    def test_strategist_path(self, game, wmap):
        game.take_item("rusty sword", wmap)
        game.current_room = "Library"
        game.take_item("ancient book", wmap)
        game.use_item("book")
        game.current_room = "Treasure Room"
        game.take_item("magic potion", wmap)
        game.use_item("potion")
        game.current_room = "Giant's Hall"
        game.attack("giant", difficulty=1.0)
        assert game.giant_defeated is True


# ── Behavior Analyzer ──────────────────────────────────────────────


class TestBehaviorAnalyzer:
    def test_update_profile_move(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("move")
        assert ba.profile["exploration"] == 1

    def test_update_profile_take(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("take")
        assert ba.profile["strategy"] == 1

    def test_update_profile_use(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("use")
        assert ba.profile["strategy"] == 1

    def test_update_profile_attack(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("attack")
        assert ba.profile["aggression"] == 1

    def test_get_action_ratios(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("move")
        ba.update_profile("move")
        ba.update_profile("attack")
        ba.update_profile("use")
        ratios = ba.get_action_ratios()
        assert ratios["explore"] == pytest.approx(0.5)
        assert ratios["attack"] == pytest.approx(0.25)
        assert ratios["use"] == pytest.approx(0.25)

    def test_get_action_ratios_empty(self):
        ba = BehaviorAnalyzer()
        ratios = ba.get_action_ratios()
        assert ratios == {"explore": 0.0, "attack": 0.0, "use": 0.0}

    def test_get_profile_summary_explorer(self):
        ba = BehaviorAnalyzer()
        for _ in range(6):
            ba.update_profile("move")
        ba.update_profile("take")
        summary = ba.get_profile_summary()
        assert "explorer" in summary.lower()

    def test_get_profile_summary_aggressor(self):
        ba = BehaviorAnalyzer()
        for _ in range(5):
            ba.update_profile("attack")
        ba.update_profile("move")
        summary = ba.get_profile_summary()
        assert "aggress" in summary.lower() or "fighter" in summary.lower()

    def test_get_profile_summary_strategist(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("take")
        ba.update_profile("use")
        ba.mark_book_read()
        ba.update_profile("attack")
        summary = ba.get_profile_summary()
        assert "strategist" in summary.lower() or "prepares" in summary.lower()

    def test_mark_book_read(self):
        ba = BehaviorAnalyzer()
        assert ba.read_book is False
        ba.mark_book_read()
        assert ba.read_book is True

    def test_read_book_before_attack_true(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("use")
        ba.mark_book_read()
        ba.update_profile("attack")
        assert ba.read_book_before_attack() is True

    def test_read_book_before_attack_false(self):
        ba = BehaviorAnalyzer()
        ba.update_profile("attack")
        ba.update_profile("use")
        assert ba.read_book_before_attack() is False


# ── Adaptation AI ──────────────────────────────────────────────────


class TestAdaptationAI:
    def test_adjust_difficulty_increases_on_aggression(self):
        ai = AdaptationAI()
        profile = {"exploration": 0, "aggression": 6, "strategy": 0}
        ai.adjust_difficulty(profile)
        assert ai.get_difficulty() == 1.5

    def test_adjust_difficulty_decreases_on_exploration(self):
        ai = AdaptationAI()
        profile = {"exploration": 0, "aggression": 0, "strategy": 6}
        ai.adjust_difficulty(profile)
        assert ai.get_difficulty() == 0.8

    def test_get_difficulty_default(self):
        ai = AdaptationAI()
        assert ai.get_difficulty() == 1.0

    def test_adapt_world_blocks_corridor_for_aggressor(self):
        ai = AdaptationAI()
        wmap = copy.deepcopy(world_map)
        profile = {"exploration": 0, "aggression": 4, "strategy": 0}
        ai.adapt_world(wmap, profile, "aggressive fighter")
        assert "north" not in wmap["Corridor"].exits
        assert ai._corridor_blocked is True

    def test_adapt_world_adds_hidden_passage_for_explorer(self):
        ai = AdaptationAI()
        wmap = copy.deepcopy(world_map)
        profile = {"exploration": 5, "aggression": 0, "strategy": 0}
        ai.adapt_world(wmap, profile, "cautious explorer")
        assert wmap["Library"].exits.get("west") == "Hidden Study"
        assert wmap["Hidden Study"].exits.get("east") == "Library"
        assert ai._hidden_passage_revealed is True


# ── Command Parser (mocked) ───────────────────────────────────────


def _make_api_response(action, target):
    """Build a mock requests.Response mimicking the Azure AI Foundry JSON."""
    body = {"content": [{"text": json.dumps({"action": action, "target": target})}]}
    resp = MagicMock()
    resp.json.return_value = body
    resp.raise_for_status = MagicMock()
    return resp


class TestCommandParser:
    def setup_method(self):
        command_cache.clear()

    @patch("command_parser.requests.post")
    def test_parse_command_valid(self, mock_post):
        mock_post.return_value = _make_api_response("move", "north")
        action, target = parse_command("go north")
        assert action == "move"
        assert target == "north"

    @patch("command_parser.requests.post")
    def test_cache_hit(self, mock_post):
        mock_post.return_value = _make_api_response("take", "rusty sword")
        parse_command("take sword")
        parse_command("take sword")
        assert mock_post.call_count == 1

    @patch("command_parser.requests.post")
    def test_api_error_key(self, mock_post):
        resp = MagicMock()
        resp.json.return_value = {"error": "rate limit"}
        resp.raise_for_status = MagicMock()
        mock_post.return_value = resp
        action, target = parse_command("go north error")
        assert action is None and target is None

    @patch("command_parser.requests.post")
    def test_malformed_json(self, mock_post):
        resp = MagicMock()
        resp.json.return_value = {"content": [{"text": "not json at all"}]}
        resp.raise_for_status = MagicMock()
        mock_post.return_value = resp
        action, target = parse_command("gibberish xyz")
        assert action is None and target is None


# ── Content Generator (mocked) ────────────────────────────────────


class TestContentGenerator:
    @patch("content_generator.requests.post")
    def test_generate_description_success(self, mock_post):
        resp = MagicMock()
        resp.json.return_value = {"content": [{"text": "A dark and eerie room."}]}
        resp.raise_for_status = MagicMock()
        mock_post.return_value = resp
        cg = ContentGenerator()
        result = cg.generate_description(
            "Starting Room",
            {},
            description="static desc",
            items=["rusty sword"],
            profile_summary="explorer",
        )
        assert result == "A dark and eerie room."

    @patch("content_generator.requests.post")
    def test_generate_description_fallback_on_error(self, mock_post):
        import requests as req

        mock_post.side_effect = req.RequestException("network error")
        cg = ContentGenerator()
        result = cg.generate_description(
            "Starting Room",
            {},
            description="static desc",
            items=[],
            profile_summary="explorer",
        )
        assert result == "static desc"


# ── End-to-End Game Loop ──────────────────────────────────────────


def _llm_response(action, target):
    """Return a mock response body for command_parser."""
    return {"content": [{"text": json.dumps({"action": action, "target": target})}]}


def _desc_response(text="You stand in a room."):
    """Return a mock response body for content_generator."""
    return {"content": [{"text": text}]}


def _run_game(input_sequence, command_responses):
    """Run main() with mocked input and a single requests.post mock.

    Uses max_tokens in the payload to distinguish command_parser (100)
    from content_generator (200) calls.  command_parser caches results
    by raw input string, so *command_responses* should only contain
    entries for the **first occurrence** of each unique input.
    """
    import contextlib
    import importlib
    import io

    command_cache.clear()
    cmd_iter = iter(command_responses)

    def _post_dispatch(url, **kwargs):
        payload = kwargs.get("json", {})
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        if payload.get("max_tokens") == 100:
            src = next(cmd_iter)
            resp.json.return_value = src.json.return_value
        else:
            resp.json.return_value = _desc_response()
        return resp

    # Ensure main module is loaded so we can patch its world_map
    import main as main_mod

    importlib.reload(main_mod)

    buf = io.StringIO()
    fresh_map = copy.deepcopy(world_map)
    with (
        patch("builtins.input", side_effect=input_sequence),
        patch("requests.post", side_effect=_post_dispatch),
        patch.object(main_mod, "world_map", fresh_map),
        contextlib.redirect_stdout(buf),
    ):
        main_mod.main()

    return buf.getvalue()


def _unique_responses(inputs, cmds):
    """Build a response list containing only the first-seen input's response.

    ``inputs`` is the list of raw player strings, ``cmds`` is a parallel
    list of (action, target) tuples.  Returns MagicMock responses only
    for the first occurrence of each unique input string (because
    command_parser caches subsequent identical strings).
    """
    seen = set()
    responses = []
    for raw, (action, target) in zip(inputs, cmds):
        if raw not in seen:
            seen.add(raw)
            r = MagicMock()
            r.json.return_value = _llm_response(action, target)
            r.raise_for_status = MagicMock()
            responses.append(r)
    return responses


class TestEndToEnd:
    def test_aggressor_path(self):
        """Take sword → use potion → navigate to Giant's Hall → attack giant (difficulty 1.5)."""
        inputs = [
            "take sword",
            "go north",
            "go east",
            "take potion",
            "use potion",
            "go west",
            "go north again",
            "go up",
            "head north",
            "attack giant",
            "hit giant",
            "strike giant",
            "fight giant",
            "swing at giant",
            "slay giant",
        ]
        cmds = [
            ("take", "rusty sword"),
            ("move", "north"),
            ("move", "east"),
            ("take", "magic potion"),
            ("use", "potion"),
            ("move", "west"),
            ("move", "north"),
            ("move", "up"),
            ("move", "north"),
            ("attack", "giant"),
            ("attack", "giant"),
            ("attack", "giant"),
            ("attack", "giant"),
            ("attack", "giant"),
            ("attack", "giant"),
        ]
        responses = _unique_responses(inputs, cmds)
        output = _run_game(inputs, responses)
        assert "defeated" in output.lower() or "giant falls" in output.lower()

    def test_strategist_path(self):
        """Take sword → read book → use potion → attack giant."""
        inputs = [
            "take sword",
            "go north",
            "go west",
            "take book",
            "use book",
            "go east",
            "head east",
            "take potion",
            "use potion",
            "walk west",
            "walk north",
            "go up",
            "head north",
            "attack giant",
        ]
        cmds = [
            ("take", "rusty sword"),
            ("move", "north"),
            ("move", "west"),
            ("take", "ancient book"),
            ("use", "book"),
            ("move", "east"),
            ("move", "east"),
            ("take", "magic potion"),
            ("use", "potion"),
            ("move", "west"),
            ("move", "north"),
            ("move", "up"),
            ("move", "north"),
            ("attack", "giant"),
        ]
        responses = _unique_responses(inputs, cmds)
        output = _run_game(inputs, responses)
        assert "defeated" in output.lower() or "topples" in output.lower()

    def test_explorer_path(self):
        """Navigate to Hidden Study → take crystal vial → use crystal vial in Giant's Hall."""
        inputs = [
            "go north",
            "go west",
            "head north",
            "go east",
            "head east",
            "go up",
            "walk west",
            "walk north",
            "take crystal vial",
            "go south",
            "walk east",
            "move north",
            "use crystal vial",
        ]
        cmds = [
            ("move", "north"),
            ("move", "west"),
            ("move", "north"),
            ("move", "east"),
            ("move", "east"),
            ("move", "up"),
            ("move", "west"),
            ("move", "north"),
            ("take", "crystal vial"),
            ("move", "south"),
            ("move", "east"),
            ("move", "north"),
            ("use", "crystal vial"),
        ]
        responses = _unique_responses(inputs, cmds)
        output = _run_game(inputs, responses)
        assert "crumbles" in output.lower() or "defeated" in output.lower()

    def test_attack_without_sword(self):
        """Attack giant without sword → giant_defeated stays False."""
        inputs = ["go north", "head north", "go up", "walk north", "attack giant", "quit"]
        cmds = [
            ("move", "north"),
            ("move", "north"),
            ("move", "up"),
            ("move", "north"),
            ("attack", "giant"),
            ("quit", "game"),
        ]
        responses = _unique_responses(inputs, cmds)
        output = _run_game(inputs, responses)
        assert "fail" in output.lower() or "without a weapon" in output.lower()
        assert "congratulations" not in output.lower()

    def test_quit(self):
        """Quit command exits cleanly."""
        r = MagicMock()
        r.json.return_value = _llm_response("quit", "game")
        r.raise_for_status = MagicMock()
        output = _run_game(["quit"], [r])
        assert "thanks for playing" in output.lower()

    def test_invalid_command(self):
        """Gibberish → fallback message, game continues."""
        # First call: gibberish returns (None, None)
        r1 = MagicMock()
        r1.json.return_value = {"content": [{"text": "???"}]}
        r1.raise_for_status = MagicMock()
        # Second call: quit
        r2 = MagicMock()
        r2.json.return_value = _llm_response("quit", "game")
        r2.raise_for_status = MagicMock()

        output = _run_game(["xyzzy", "quit"], [r1, r2])
        assert "do not understand" in output.lower()
        assert "thanks for playing" in output.lower()
