import pygame
import os

WIDTH, HEIGHT = 240, 320
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Mock Game")

SCREEN_BACKGROUND_COLOR = (10, 40, 15)
SHIP_WIDTH, SHIP_HEIGHT = 16, 16
YELLOW_SHIP_IMAGE = pygame.image.load(os.path.join("assets", "spaceship_yellow.png"))
YELLOW_SHIP = pygame.transform.scale(YELLOW_SHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT))
YELLOW_SHIP = pygame.transform.rotate(YELLOW_SHIP, 90)  # face right
RED_SHIP_IMAGE = pygame.image.load(os.path.join("assets", "spaceship_red.png"))
RED_SHIP = pygame.transform.scale(RED_SHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT))
RED_SHIP = pygame.transform.rotate(RED_SHIP, -90)  # face left


def draw_window(red, yellow):
    WIN.fill(SCREEN_BACKGROUND_COLOR)
    WIN.blit(YELLOW_SHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SHIP, (red.x, red.y))
    pygame.display.update()


def main():
    yellow = pygame.Rect(WIDTH//4-SHIP_WIDTH, HEIGHT//2, SHIP_WIDTH, SHIP_HEIGHT)
    red = pygame.Rect(WIDTH-WIDTH//4, HEIGHT//2, SHIP_WIDTH, SHIP_HEIGHT)
    clock = pygame.time.Clock()
    run = True

    VEL = 2

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
        if keys_pressed[pygame.K_UP]:
            red.y -= VEL
        if keys_pressed[pygame.K_DOWN]:
            red.y += VEL
        draw_window(red, yellow)

    pygame.quit()


if __name__ == "__main__":
    main()