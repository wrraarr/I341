import pygame

def main():
    pygame.init()
    screen_width, screen_height = 1000, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Font Test")

    # list fonts on your system
    print(pygame.font.get_fonts())

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Load the system font correctly
    font_name = "bentonsans"
    font_size = 22
    font = pygame.font.SysFont(font_name, font_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        text_surface = font.render('Hello, BentonSans!', True, BLACK)
        screen.blit(text_surface, (50, 50))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()