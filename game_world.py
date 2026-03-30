# game_world.py


class Room:
    """A location in the game world that the player can visit.

    Attributes:
        name: Unique display name of the room.
        description: Atmospheric text shown when the player enters.
        items: List of Item objects currently in the room.
        exits: Dict mapping direction strings to destination room names.
    """

    def __init__(self, name, description, items=None, exits=None):
        """Initialize a Room with a name, description, items, and exit directions.

        name (str): Unique name of the room.
        description (str): Atmospheric text description of the room.
        items (list, optional): List of Item objects initially in the room. Defaults to [].
        exits (dict, optional): Mapping of direction -> room name. Defaults to {}.

        """
        self.name = name
        self.description = description
        self.items = items if items else []
        self.exits = exits if exits else {}


class Item:
    """An object that can be found, carried, and optionally used by the player.

    Attributes:
        name: Display name of the item.
        description: Text description of the item's appearance or purpose.
        usable: Whether the item can be activated with the 'use' command.
    """

    def __init__(self, name, description, usable=False):
        """Initialize an Item with a name, description, and usability flag.

        name (str): Display name of the item.
        description (str): Text description of the item's appearance/purpose.
        usable (bool, optional): Whether the item can be used with the 'use' command. Defaults to False.

        """
        self.name = name
        self.description = description
        self.usable = usable


# ── Items ────────────────────────────────────────────────────────────

rusty_sword = Item("rusty sword", "An old sword, but it might still be useful.")
magic_potion = Item("magic potion", "A potion that might give you strength.", usable=True)
ancient_book = Item("ancient book", "A book that might contain useful information.", usable=True)
key = Item("key", "A key that might unlock something important.", usable=True)
silver_shield = Item("silver shield", "A battered shield that still gleams faintly.", usable=True)
torch = Item("torch", "A lit torch that pushes back the darkness.", usable=True)
crystal_vial = Item("crystal vial", "A vial of luminous liquid — the Giant's own draft, distilled.", usable=True)
iron_helm = Item("iron helm", "A heavy helm that makes you feel invincible.", usable=True)

# ── Rooms (15 total) ────────────────────────────────────────────────

starting_room = Room(
    name="Starting Room",
    description=(
        "A small, dimly lit chamber carved from grey stone. A single candle "
        "gutters on a shelf, casting restless shadows across the walls. The air "
        "smells of damp earth and old iron. A wooden door to the north stands ajar."
    ),
    items=[rusty_sword],
    exits={"north": "Corridor"},
)

corridor = Room(
    name="Corridor",
    description=(
        "A long passage stretches before you, its vaulted ceiling lost in darkness. "
        "Faded tapestries line the walls, depicting scenes of giants feasting at an "
        "enormous table. Doors branch east, west, and north, while the south leads "
        "back to where you started."
    ),
    exits={
        "south": "Starting Room",
        "east": "Treasure Room",
        "west": "Library",
        "north": "Great Staircase",
    },
)

treasure_room = Room(
    name="Treasure Room",
    description=(
        "Gold coins and faceted jewels spill across the floor in careless heaps. "
        "A marble pedestal rises from the centre of the glittering mess, and atop it "
        "a magic potion pulses with an inner blue light. The air hums with latent power."
    ),
    items=[magic_potion],
    exits={"west": "Corridor"},
)

library = Room(
    name="Library",
    description=(
        "Shelves of ancient books climb to a ceiling you cannot see, their spines "
        "cracked and faded. Dust motes drift in a shaft of pale light from an unseen "
        "window. One volume — 'The Legend of the Giant' — lies open on a reading stand, "
        "as though someone left mid-sentence."
    ),
    items=[ancient_book],
    exits={"east": "Corridor", "north": "Archives"},
)

archives = Room(
    name="Archives",
    description=(
        "Rows of iron filing cabinets stand like sentinels in this cold, echoing room. "
        "Scrolls and maps spill from half-open drawers. A faded map on the wall marks a "
        "passage behind the Library shelves — if one knew where to look."
    ),
    exits={"south": "Library", "east": "Servants Passage"},
)

servants_passage = Room(
    name="Servants Passage",
    description=(
        "A narrow, low-ceilinged tunnel that the castle servants once used to move unseen. "
        "The stones are worn smooth by centuries of hurried footsteps. It connects the "
        "archives to the great staircase without passing through the main halls."
    ),
    exits={"west": "Archives", "east": "Great Staircase"},
)

great_staircase = Room(
    name="Great Staircase",
    description=(
        "A sweeping staircase of white marble spirals upward into shadow. Each step is "
        "wide enough for a giant's boot. Carvings of vines and serpents wind along the "
        "banisters, their stone eyes seeming to follow you as you climb."
    ),
    exits={
        "south": "Corridor",
        "west": "Servants Passage",
        "up": "Upper Landing",
    },
)

upper_landing = Room(
    name="Upper Landing",
    description=(
        "The staircase opens onto a broad landing overlooking the hall below. Three "
        "corridors radiate outward like the spokes of a wheel — north to the Giant's "
        "Hall, east to the Armoury, and west to the Observatory."
    ),
    exits={
        "down": "Great Staircase",
        "north": "Giant's Hall",
        "east": "Armoury",
        "west": "Observatory",
    },
)

armoury = Room(
    name="Armoury",
    description=(
        "Racks of oversized weapons line the walls — halberds, maces, and swords built "
        "for hands three times your size. A single human-sized silver shield hangs on a "
        "hook, almost lost among the giant's arsenal. Cobwebs bridge the weapon racks."
    ),
    items=[silver_shield],
    exits={"west": "Upper Landing"},
)

observatory = Room(
    name="Observatory",
    description=(
        "A domed room open to the night sky through a cracked glass ceiling. A massive "
        "brass telescope points at the stars, its lens clouded with age. Star charts "
        "cover every surface, and the wind whispers through the broken panes."
    ),
    items=[torch],
    exits={"east": "Upper Landing", "north": "Hidden Study"},
)

hidden_study = Room(
    name="Hidden Study",
    description=(
        "Behind a revolving bookcase you find a small, secret study. A desk holds a "
        "crystal vial filled with luminous liquid — the Giant's own draft, distilled "
        "to its purest form. This is the weapon of legend, the thing the giant fears "
        "most: his own strength turned against him."
    ),
    items=[crystal_vial],
    exits={"south": "Observatory"},
)

giants_hall = Room(
    name="Giant's Hall",
    description=(
        "A cavernous hall stretches before you, its ceiling lost in darkness high above. "
        "An enormous throne of twisted iron dominates the far end. The giant sits upon it, "
        "chest rising and falling in uneasy sleep, a heavy key on a chain around his neck. "
        "The floor trembles faintly with each of his breaths."
    ),
    items=[key],
    exits={"south": "Upper Landing", "east": "Throne Antechamber"},
)

throne_antechamber = Room(
    name="Throne Antechamber",
    description=(
        "A side chamber adjoining the Giant's Hall. Tattered banners hang from the rafters "
        "bearing the giant's crest — a fist clutching a goblet. A heavy iron door to the "
        "north is locked, but a keyhole glints in the torchlight."
    ),
    exits={"west": "Giant's Hall", "north": "Victory Chamber"},
)

victory_chamber = Room(
    name="Victory Chamber",
    description=(
        "Beyond the iron door lies a small, luminous chamber. Sunlight streams through a "
        "high window, illuminating a golden goblet on a stone altar — the Giant's Drink "
        "itself. Whoever claims it commands the castle."
    ),
    exits={"south": "Throne Antechamber"},
)

dungeon = Room(
    name="Dungeon",
    description=(
        "Damp stone walls press close in this underground cell. Chains hang from iron "
        "rings, and the only light comes from a grate far above. An iron helm rests "
        "in the corner, forgotten by some earlier prisoner."
    ),
    items=[iron_helm],
    exits={"up": "Starting Room"},
)

# ── World Map ────────────────────────────────────────────────────────

world_map = {
    "Starting Room": starting_room,
    "Corridor": corridor,
    "Treasure Room": treasure_room,
    "Library": library,
    "Archives": archives,
    "Servants Passage": servants_passage,
    "Great Staircase": great_staircase,
    "Upper Landing": upper_landing,
    "Armoury": armoury,
    "Observatory": observatory,
    "Hidden Study": hidden_study,
    "Giant's Hall": giants_hall,
    "Throne Antechamber": throne_antechamber,
    "Victory Chamber": victory_chamber,
    "Dungeon": dungeon,
}
