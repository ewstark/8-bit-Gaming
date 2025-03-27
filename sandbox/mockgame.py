import pygame
import os

# global vars
g_verbose = False

screen_width, screen_height = 320, 240
WIN = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Mock Game")

screen_bg_color = (10, 40, 15)
ship_sprite_width, ship_sprite_screen_height = 16, 16
YELLOW_SHIP_IMAGE = pygame.image.load(os.path.join("assets", "spaceship_yellow.png"))
YELLOW_SHIP = pygame.transform.scale(YELLOW_SHIP_IMAGE, (ship_sprite_width, ship_sprite_screen_height))

pygame.mixer.init()
laser_sound = pygame.mixer.Sound(os.path.join("assets", "laserShoot_8bit_22kHz_mono.wav"))

def draw_window (yellow):
    WIN.fill(screen_bg_color)
    WIN.blit(YELLOW_SHIP, (yellow.x, yellow.y))
    pygame.display.update()


class audio_interface:
    # Assume a register layout that occurs in one contiguous address range that is twice the size,
    # in bytes, as the number of interface channels.  The first half of that range assigns a new
    # volume to the addressed channel and queues the event for processing.  The second half is the
    # patch assigned to each channel.
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
    yellow = pygame.Rect(screen_width//4 - ship_sprite_width, screen_height//2, ship_sprite_width, ship_sprite_screen_height)
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