import pygame
import math
import time


class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 74)
        self.button_play = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 25, 200, 50)

    def start(self, screen):
        while True:
            screen.fill((0, 0, 0))
            text = self.font.render("Главное меню", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
            screen.blit(text, text_rect)

            pygame.draw.rect(screen, (0, 0, 200), self.button_play)
            text_play = self.font.render("Играть", True, (0, 0, 0))
            text_rect_pl = text_play.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(text_play, text_rect_pl)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_play.collidepoint(pygame.mouse.get_pos()):
                        return

            pygame.display.flip()


class GameProcess:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.ship_image1 = pygame.image.load("Корабль_1.png").convert_alpha()
        self.ship_image2 = pygame.image.load("Корабль_2.png").convert_alpha()
        self.ship_image3 = pygame.image.load("Корабль_3.png").convert_alpha()
        self.ship_image1_1 = pygame.image.load("Корабль_1_1.png").convert_alpha()
        self.ship_image2_1 = pygame.image.load("Корабль_2_1.png").convert_alpha()
        self.ship_image3_1 = pygame.image.load("Корабль_3_1.png").convert_alpha()

        self.ship_images = [self.ship_image1, self.ship_image2, self.ship_image3, self.ship_image1_1,
                            self.ship_image2_1, self.ship_image3_1]

        for i in range(len(self.ship_images)):
            self.ship_images[i] = pygame.transform.scale(self.ship_images[i], (150, 100))

        self.ship1 = self.ship_images[0].get_rect(center=(screen_width // 2, screen_height // 2))
        self.ship2 = self.ship_images[3].get_rect(center=(screen_width // 4, screen_height // 4))

        self.ship_side = 0
        self.ship_side2 = 0
        self.ship_speed = 0.4
        self.spin_speed = 0.25
        self.ship_x_offset = 0
        self.ship_y_offset = 0
        self.ship_x_offset2 = 0
        self.ship_y_offset2 = 0

        self.image_index = 0
        self.last_switch_time = time.time()
        self.switch_interval = 0.01

        self.button_back = pygame.Rect(20, 20, 100, 50)
        self.font = pygame.font.Font(None, 36)

    def play(self, screen):
        fly = True
        while fly:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fly = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_back.collidepoint(pygame.mouse.get_pos()):
                        return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if time.time() - self.last_switch_time >= self.switch_interval:
                    self.image_index = 1 - self.image_index
                    self.last_switch_time = time.time()

                current_image = [self.ship_images[1], self.ship_images[2]][self.image_index]
                self.ship_x_offset += self.ship_speed * math.cos(math.radians(self.ship_side))
                self.ship_y_offset -= self.ship_speed * math.sin(math.radians(self.ship_side))
                self.ship_x_offset %= self.screen_width
                self.ship_y_offset %= self.screen_height
            else:
                current_image = self.ship_images[0]
                self.ship_side += self.spin_speed

            if keys[pygame.K_RETURN]:
                if time.time() - self.last_switch_time >= self.switch_interval:
                    self.image_index = 1 - self.image_index
                    self.last_switch_time = time.time()

                current_image_2 = [self.ship_images[4], self.ship_images[5]][self.image_index]

                self.ship_x_offset2 += self.ship_speed * math.cos(math.radians(self.ship_side2))
                self.ship_y_offset2 -= self.ship_speed * math.sin(math.radians(self.ship_side2))
                self.ship_x_offset2 %= self.screen_width
                self.ship_y_offset2 %= self.screen_height
            else:
                current_image_2 = self.ship_images[3]
                self.ship_side2 += self.spin_speed

            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, '#b8860b', (1000, 1000), 270, 0)
            pygame.draw.circle(screen, '#b5800d', (1000, 1000), 270, 50)
            pygame.draw.circle(screen, '#b8860b', (0, 0), 270, 0)
            pygame.draw.circle(screen, '#b5800d', (0, 0), 270, 50)

            rotated_ship = pygame.transform.rotate(current_image, self.ship_side)
            x = self.ship1.centerx + self.ship_x_offset
            y = self.ship1.centery + self.ship_y_offset
            x_draw = x % self.screen_width
            y_draw = y % self.screen_height
            if x < 0:
                x_draw += self.screen_width
            if y < 0:
                y_draw += self.screen_height
            rotated_rect = rotated_ship.get_rect(center=(x_draw, y_draw))
            screen.blit(rotated_ship, rotated_rect)

            rotated_ship2 = pygame.transform.rotate(current_image_2, self.ship_side2)
            x2 = self.ship2.centerx + self.ship_x_offset2
            y2 = self.ship2.centery + self.ship_y_offset2
            x_draw2 = x2 % self.screen_width
            y_draw2 = y2 % self.screen_height
            if x2 < 0:
                x_draw2 += self.screen_width
            if y2 < 0:
                y_draw2 += self.screen_height
            rotated_rect2 = rotated_ship2.get_rect(center=(x_draw2, y_draw2))
            screen.blit(rotated_ship2, rotated_rect2)

            pygame.draw.rect(screen, '#b8860b', self.button_back)
            text_back = self.font.render("Назад", True, (0, 0, 0))
            screen.blit(text_back, (30, 30))

            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen_width = 1000
    screen_height = 1000
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Космос")

    menu = Menu(screen_width, screen_height)
    game_process = GameProcess(screen_width, screen_height)

    while True:
        menu.start(screen)
        game_process.play(screen)