# Canary Crush
# by Eric W. Stark
# A simple game created in PyGame to test basic arcade game mechanisms
# such as low-res sprite-based pixel graphics and channel-based asynchronous
# audio events.

import pygame
import os

from enum import Enum
from dataclasses import dataclass, field

# verbose debug output while game is running
g_verbose = False

# basic constants
g_display_width, g_display_height = 320, 240
g_cell_sprite_width, g_cell_sprite_height = 16, 16
g_player_velocity = 2
g_color_screen_bg = (10, 30, 20)


@dataclass
class Point:
    x : int = 0
    y : int = 0

# The home cell for the player to start each round.
g_home_cell = Point(7, 7)

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def image_at(self, x, y, dx, dy, colorkey = None):
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(x, y, x+dx, y+dy)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

class ActorType (Enum):
    PLAYER = 0
    BLOCK = 1
    ENEMY = 2

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
    type          : ActorType
    state         : ActorState = ActorState.STATIONARY
    last_cell     : Point = g_home_cell
    next_cell     : Point = g_home_cell
    facing        : Direction = Direction.DOWN
    sprite_width  : int = g_cell_sprite_width
    sprite_height : int = g_cell_sprite_height
    position      : Point = Point(last_cell.x * sprite_width, last_cell.y * sprite_height)
    
    def load_sprites (self, filename):
        self.canary_sprite_sheet = SpriteSheet(filename)
        self.sprite = self.canary_sprite_sheet.image_at(0, 0, self.sprite_width, self.sprite_height, -1)

    def get_sprite (self):
        return self.sprite

    def set_direction(self, direction):
        self.facing = direction
        if direction == Direction.UP:
            if self.last_cell.y > 1:
                self.next_cell.y -= 1
                self.state = ActorState.MOVING
        elif direction == Direction.DOWN:
            if self.last_cell.y < 13:
                self.next_cell.y += 1
                self.state = ActorState.MOVING
        elif direction == Direction.LEFT:
            if self.last_cell.x > 1:
                self.next_cell.x -= 1
                self.state = ActorState.MOVING
        elif direction == Direction.RIGHT:
            if self.last_cell.x < 13:
                self.next_cell.x += 1
                self.state = ActorState.MOVING

    def update_position (self):
        if self.state == ActorState.MOVING:
            if self.facing == Direction.UP:
                self.position.y -= g_player_velocity
            elif self.facing == Direction.DOWN:
                self.position.y += g_player_velocity
            elif self.facing == Direction.LEFT:
                self.position.x -= g_player_velocity
            elif self.facing == Direction.RIGHT:
                self.position.x += g_player_velocity
            # once we reach a cell position on the grid, we're done moving
            if self.position.y % g_cell_sprite_height == 0 and self.position.x % g_cell_sprite_width == 0:
                self.state = ActorState.STATIONARY
                self.last_cell = self.next_cell


def draw_window (player, blocks, enemies):
    g_pygame_display.fill(g_color_screen_bg)
    g_pygame_display.blit(player.get_sprite(), (player.position.x, player.position.y))
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


def main (args):
    clock = pygame.time.Clock()
    run = True
    fire_held = False

    # setup actors:
    # player
    player = Actor(ActorType.PLAYER)
    player.load_sprites(os.path.join("assets", "canary_sheet.png"))
    # blocks
    blocks = []
    blocks.append(Actor(ActorType.BLOCK, last_cell=(4,4)))
    # enemies
    enemies = []

    while run:
        clock.tick(60) # limit update rate to 60 Hz
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        player.update_position()

        keys_pressed = pygame.key.get_pressed()

        if player.state == ActorState.STATIONARY:
            if keys_pressed[pygame.K_w] and not keys_pressed[pygame.K_s]: # up
                player.set_direction(Direction.UP)
            elif keys_pressed[pygame.K_s] and not keys_pressed[pygame.K_w]: # down
                player.set_direction(Direction.DOWN)
            elif keys_pressed[pygame.K_a] and not keys_pressed[pygame.K_d]: # left
                player.set_direction(Direction.LEFT)
            elif keys_pressed[pygame.K_d] and not keys_pressed[pygame.K_a]: # right
                player.set_direction(Direction.RIGHT)
 
        if keys_pressed[pygame.K_SPACE]:
            if not fire_held:
                fire_held = True
                pygame.mixer.Sound.play(laser_sound)
        else:
            fire_held = False

        draw_window(player, blocks, enemies)

    pygame.quit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="8-bit Arcade Game Mock")
    parser.add_argument("config_filename", type=str, nargs='?', default="game.config", help="game configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose debug output")
    args = parser.parse_args()
    g_verbose = args.verbose

    # create window for game using native (low) resolution but scaled-up as possible
    g_pygame_display = pygame.display.set_mode((g_display_width, g_display_height), 
                                           pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Canary Crush")

    # initialize sound interface
    pygame.mixer.init()
    laser_sound = pygame.mixer.Sound(os.path.join("assets", "laserShoot_8bit_22kHz_mono.wav"))

    main(args)