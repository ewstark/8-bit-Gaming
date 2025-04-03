# Canary Crush
# by Eric W. Stark
# A simple game created in PyGame to test 

import pygame
import os

from enum import Enum
from dataclasses import dataclass, field

# verbose debug output while game is running
g_verbose = False

# basic constants
g_display_width, g_display_height = 320, 240
g_cell_sprite_width, g_cell_sprite_height = 16, 16

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

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class PlayerState(Enum):
    STATIONARY = 0
    MOVING = 1
    PUSHING = 2
    DYING = 3
    DEAD = 4

@dataclass
class Player:
    state         : PlayerState = PlayerState.STATIONARY
    last_cell     : Point = g_home_cell
    next_cell     : Point = g_home_cell
    facing        : Direction = Direction.DOWN
    sprite_width  : int = g_cell_sprite_width
    sprite_height : int = g_cell_sprite_height
    position      : Point = Point(g_home_cell.x * g_cell_sprite_width, 
                                  g_home_cell.y * g_cell_sprite_height)

# create window for game using native (low) resolution but scaled-up as possible
g_pygame_display = pygame.display.set_mode((g_display_width, g_display_height), 
                                           pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Canary Crush")

canary_sprite_sheet = SpriteSheet(os.path.join("assets", "canary_sheet.png"))

canary_sprite = canary_sprite_sheet.image_at(0, 0, g_cell_sprite_width, g_cell_sprite_height)

pygame.mixer.init()
laser_sound = pygame.mixer.Sound(os.path.join("assets", "laserShoot_8bit_22kHz_mono.wav"))

def draw_window (yellow):
    g_pygame_display.fill(g_color_screen_bg)
    g_pygame_display.blit(canary_sprite, (yellow.x, yellow.y))
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
    yellow = pygame.Rect(g_display_width//4 - g_cell_sprite_width, g_display_height//2, g_cell_sprite_width, g_cell_sprite_height)
    clock = pygame.time.Clock()
    run = True
    VEL = 2
    fire_held = False

    while run:
        clock.tick(60) # limit update rate to 60 Hz
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w]:
            yellow.y -= VEL
        if keys_pressed[pygame.K_s]:
            yellow.y += VEL
        if keys_pressed[pygame.K_a]:
            yellow.x -= VEL
        if keys_pressed[pygame.K_d]:
            yellow.x += VEL
        if keys_pressed[pygame.K_SPACE]:
            if not fire_held:
                fire_held = True
                pygame.mixer.Sound.play(laser_sound)
        else:
            fire_held = False
        draw_window(yellow)

    pygame.quit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="8-bit Arcade Game Mock")
    parser.add_argument("config_filename", type=str, nargs='?', default="game.config", help="game configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose debug output")
    args = parser.parse_args()
    g_verbose = args.verbose
    main(args)