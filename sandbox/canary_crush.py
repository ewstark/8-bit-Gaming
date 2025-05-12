# Canary Crush
# by Eric W. Stark
# A simple game created in PyGame to test basic arcade game mechanisms
# such as low-res sprite-based pixel graphics and channel-based asynchronous
# audio events.

import pygame
import os

from enum import Enum
from dataclasses import dataclass, field
from copy import copy

# verbose debug output while game is running
g_verbose = False

# basic constants
g_display_width, g_display_height = 320, 240
g_cell_sprite_width, g_cell_sprite_height = 16, 16
g_player_velocity = 2
g_color_screen_bg = (10, 30, 20)

# user-input status
g_push_button_held = False

@dataclass
class Point:
    x : int = 0
    y : int = 0

# The home cell for the player to start each round.
g_home_cell = Point(7, 7)

class SpriteSheet:
    def __init__ (self, filename, width=16, height=16):
        self.sheet = pygame.image.load(filename).convert()
        self.width = width
        self.height = height

    def image_at_index (self, index, colorkey = None):
        # Loads image from horizontal sheet location by zero-based index
        rect = pygame.Rect(index * self.width, 0, self.width, self.height)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

# indices for sprites stored in horizontal strip in the sprite-sheet
SPRITE_INDEX_CANARY_RIGHT_NORMAL = 0
SPRITE_INDEX_CANARY_RIGHT_FLAP   = 1
SPRITE_INDEX_CANARY_RIGHT_WALK1  = 2   # future
SPRITE_INDEX_CANARY_RIGHT_WALK2  = 3   # future
SPRITE_INDEX_CANARY_UP_NORMAL    = 4
SPRITE_INDEX_CANARY_UP_FLAP      = 5
SPRITE_INDEX_BLOCK_NORMAL        = 6
SPRITE_INDEX_ENEMY_NORMAL        = 7

class ActorType (Enum):
    PLAYER = 0
    ENEMY = 1
    BLOCK = 2
    VENTILATION = 3

class ActorState (Enum):
    STATIONARY = 0
    MOVING = 1
    PUSHING = 2
    DYING = 3
    DEAD = 4

class Direction (Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

@dataclass
class Actor:
    type         : ActorType
    sprites      : dict[int,object]
    current_cell : Point
    next_cell    : Point = None
    state        : ActorState = ActorState.STATIONARY
    facing       : Direction = Direction.RIGHT
    phase        : int = 0

    def __post_init__ (self):
        self.sprite_width = g_cell_sprite_width
        self.sprite_height = g_cell_sprite_height
        self.position = Point(self.current_cell.x * self.sprite_width, self.current_cell.y * self.sprite_height)

    def get_sprite (self):
        return self.sprites[next(iter(self.sprites))]

    def set_direction (self, direction):
        pass

    def update_position (self):
        pass


@dataclass
class PlayerActor (Actor):
    def get_sprite (self):
        return self.sprites[self.facing]

    def set_direction (self, direction):
        self.facing = direction
        possible_next_cell = copy(self.current_cell)
        if direction == Direction.UP:
            possible_next_cell.y -= 1
        elif direction == Direction.DOWN:
            possible_next_cell.y += 1
        elif direction == Direction.LEFT:
            possible_next_cell.x -= 1
        elif direction == Direction.RIGHT:
            possible_next_cell.x += 1
        # make sure we stay on board
        if 1 <= possible_next_cell.x <= 13 and 1 <= possible_next_cell.y <= 13:
            if find_block(possible_next_cell):
                pass
            elif find_enemy(possible_next_cell):
                self.state = ActorState.DEAD
            else:
                self.next_cell = possible_next_cell
                self.state = ActorState.MOVING

    def update_position (self):
        if self.state == ActorState.MOVING:
            if self.facing == Direction.UP:
                self.position.y -= g_player_velocity
                self.phase += 1
            elif self.facing == Direction.DOWN:
                self.position.y += g_player_velocity
                self.phase += 1
            elif self.facing == Direction.LEFT:
                self.position.x -= g_player_velocity
                self.phase += 1
            elif self.facing == Direction.RIGHT:
                self.position.x += g_player_velocity
                self.phase += 1
            # once we reach a cell position on the grid, we're done moving
            if self.position.y % g_cell_sprite_height == 0 and self.position.x % g_cell_sprite_width == 0:
                self.state = ActorState.STATIONARY
                self.phase = 0
                self.current_cell = copy(self.next_cell)


def draw_window ():
    global g_display_bg, g_player, g_blocks, g_enemies
    g_pygame_display.blit(g_display_bg, (0, 0))
    for b in g_blocks:
        g_pygame_display.blit(b.get_sprite(), (b.position.x, b.position.y))
    for e in g_enemies:
        g_pygame_display.blit(e.get_sprite(), (e.position.x, e.position.y))
    g_pygame_display.blit(g_player.get_sprite(), (g_player.position.x, g_player.position.y))
    pygame.display.update()

class audio_interface:
    # Assume a register layout that occurs in one contiguous address range that is twice the size,
    # in bytes, as the number of interface channels.  The first half of that range queues events.
    # The second half assigns the patch number (0-255) to each channel.
    def __init__ (self, num_channels=16, channel_assignments=None, base_address=0x4000):
        assert(num_channels > 0)
        assert(base_address >= 0)
        self.num_channels = num_channels
        if channel_assignments is None:
            self.channel_assignments = [i for i in range(num_channels)]
        else:
            assert(len(channel_assignments) == num_channels)
            self.channel_assignments = [i for i in channel_assignments]
        self.base_address = base_address
        # assign initial channel patches
        for channel in range(self.num_channels):
            self.assign_channel_patch(channel, self.channel_assignments[channel])

    def assign_channel_patch (self, channel, patch):
        assert(0 <= channel < self.num_channels)
        assert(0 <= patch < 256)
        self.channel_assignments[channel] = patch
        self._write_register(self.base_address + self.num_channels + channel, patch)

    def trigger_channel (self, channel, volume):
        assert(0 <= channel < self.num_channels)
        assert(0 <= volume < 256)
        self._write_register(self.base_address + channel, volume)

    def _write_register (address, value):
        # set [address] = value
        pass

def find_block (pos):
    global g_blocks
    for b in g_blocks:
        if b.current_cell == pos:
            return b
    return None

def find_enemy (pos):
    global g_enemies
    for e in g_enemies:
        if e.current_cell == pos:
            return e
    return None

def main (args):
    global g_display_bg, g_player, g_blocks, g_enemies
    clock = pygame.time.Clock()
    run = True

    g_display_bg = pygame.image.load(os.path.join("assets", "canary_crush_bg.png")).convert()

    sprite_sheet = SpriteSheet(os.path.join("assets", "canary_sheet.png"))
    player_sprites = {}
    player_sprites[Direction.UP] = sprite_sheet.image_at_index(SPRITE_INDEX_CANARY_UP_NORMAL, -1)
    player_sprites[Direction.RIGHT] = sprite_sheet.image_at_index(SPRITE_INDEX_CANARY_RIGHT_NORMAL, -1)
    player_sprites[Direction.DOWN] = pygame.transform.flip(sprite_sheet.image_at_index(SPRITE_INDEX_CANARY_UP_NORMAL, -1), False, True)
    player_sprites[Direction.LEFT] = pygame.transform.flip(sprite_sheet.image_at_index(SPRITE_INDEX_CANARY_RIGHT_NORMAL, -1), True, False)

    g_player = PlayerActor(ActorType.PLAYER, player_sprites, g_home_cell)

    g_blocks = []
    g_blocks.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_BLOCK_NORMAL, -1)}, Point(4,4)))
    g_blocks.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_BLOCK_NORMAL, -1)}, Point(4,5)))
    g_blocks.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_BLOCK_NORMAL, -1)}, Point(4,6)))
    g_blocks.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_BLOCK_NORMAL, -1)}, Point(5,4)))
    g_blocks.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_BLOCK_NORMAL, -1)}, Point(6,6)))

    g_enemies = []
    g_enemies.append(Actor(ActorType.BLOCK, {0: sprite_sheet.image_at_index(SPRITE_INDEX_ENEMY_NORMAL, -1)}, Point(4,7)))

    while run:
        clock.tick(60) # limit update rate to 60 Hz
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys_pressed = pygame.key.get_pressed()
        if g_player.state == ActorState.STATIONARY:
            if keys_pressed[pygame.K_w] and not keys_pressed[pygame.K_s]: # up
                g_player.set_direction(Direction.UP)
            elif keys_pressed[pygame.K_s] and not keys_pressed[pygame.K_w]: # down
                g_player.set_direction(Direction.DOWN)
            elif keys_pressed[pygame.K_a] and not keys_pressed[pygame.K_d]: # left
                g_player.set_direction(Direction.LEFT)
            elif keys_pressed[pygame.K_d] and not keys_pressed[pygame.K_a]: # right
                g_player.set_direction(Direction.RIGHT)
        if keys_pressed[pygame.K_SPACE]: # push
            if not g_push_button_held and g_player.state == ActorState.STATIONARY:
                g_push_button_held = True
                pygame.mixer.Sound.play(canary_sound_push)
                g_player.state = ActorState.PUSHING
        else:
            if g_player.state == ActorState.PUSHING:
                g_player.state = ActorState.STATIONARY
            g_push_button_held = False

        g_player.update_position()

        draw_window()

    pygame.quit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="8-bit Arcade Game Mock")
    parser.add_argument("config_filename", type=str, nargs='?', default="game.config", help="game configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose debug output")
    args = parser.parse_args()
    g_verbose = args.verbose

    # create window for game using native (low) resolution but scaled-up as possible
    g_pygame_display = pygame.display.set_mode((g_display_width, g_display_height), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Canary Crush")

    # initialize sound interface
    pygame.mixer.init()
    canary_sound_push = pygame.mixer.Sound(os.path.join("assets", "canary_push.wav"))

    main(args)