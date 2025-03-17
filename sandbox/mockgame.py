import pygame
import os

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mock Game")

SCREEN_BACKGROUND_COLOR = (100, 255, 200)

GAME_FPS = 60

SHIP_WIDTH, SHIP_HEIGHT = 55, 40

YELLOW_SHIP_IMAGE = pygame.image.load(os.path.join("assets", "spaceship_yellow.png"))
YELLOW_SHIP = pygame.transform.scale(YELLOW_SHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT))
YELLOW_SHIP = pygame.transform.rotate(YELLOW_SHIP, 90)

RED_SHIP_IMAGE = pygame.image.load(os.path.join("assets", "spaceship_red.png"))
RED_SHIP = pygame.transform.scale(RED_SHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT))
RED_SHIP = pygame.transform.rotate(RED_SHIP, -90)


def draw_window(red, yellow):
    WIN.fill(SCREEN_BACKGROUND_COLOR)
    WIN.blit(YELLOW_SHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SHIP, (red.x, red.y))
    pygame.display.update()


def main():
    red = pygame.Rect(700, 300, SHIP_WIDTH, SHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SHIP_WIDTH, SHIP_HEIGHT)
    clock = pygame.time.Clock()
    run = True
    VEL = 2

    while run:
        clock.tick(GAME_FPS)

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