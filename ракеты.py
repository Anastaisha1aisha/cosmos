import pygame
import math
import time

if __name__ == '__main__':
    pygame.init()
    screen_width = 1000
    screen_height = 1000
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Космос")

    ship_image1 = pygame.image.load("Корабль_1.png").convert_alpha()
    ship_image2 = pygame.image.load("Корабль_2.png").convert_alpha()
    ship_image3 = pygame.image.load("Корабль_3.png").convert_alpha()
    ship_image1_1 = pygame.image.load("Корабль_1_1.png").convert_alpha()
    ship_image2_1 = pygame.image.load("Корабль_2_1.png").convert_alpha()
    ship_image3_1 = pygame.image.load("Корабль_3_1.png").convert_alpha()

    ship_images = [ship_image1, ship_image2, ship_image3, ship_image1_1, ship_image2_1, ship_image3_1]

    for i in range(len(ship_images)):
        ship_images[i] = pygame.transform.scale(ship_images[i], (150, 100))

    ship_image1, ship_image2, ship_image3, ship_image1_1, ship_image2_1, ship_image3_1 = ship_images

    def game_process():

        ship = ship_image1.get_rect(center=(screen_width // 2, screen_height // 2))
        ship2 = ship_image1_1.get_rect(center=(screen_width // 4, screen_height // 4))

        ship_side = 0
        ship_side2 = 0
        ship_speed = 0.4  # перемещение
        spin_speed = 0.25  # вращение

        ship_x_offset = 0
        ship_y_offset = 0
        ship_x_offset2 = 0
        ship_y_offset2 = 0

        current_image = ship_image1
        current_image_2 = ship_image1_1
        image_index = 0
        last_switch_time = time.time()
        switch_interval = 0.01

        fly = True
        while fly:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fly = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if time.time() - last_switch_time >= switch_interval:
                    image_index = 1 - image_index
                    last_switch_time = time.time()

                current_image = [ship_image2, ship_image3][image_index]
                ship_x_offset += ship_speed * math.cos(math.radians(ship_side))
                ship_y_offset -= ship_speed * math.sin(math.radians(ship_side))
                ship_x_offset %= screen_width
                ship_y_offset %= screen_height

            else:
                current_image = ship_image1
                ship_side += spin_speed

            if keys[pygame.K_RETURN]:
                if time.time() - last_switch_time >= switch_interval:
                    image_index = 1 - image_index
                    last_switch_time = time.time()

                current_image_2 = [ship_image2_1, ship_image3_1][image_index]

                ship_x_offset2 += ship_speed * math.cos(math.radians(ship_side2))
                ship_y_offset2 -= ship_speed * math.sin(math.radians(ship_side2))
                ship_x_offset2 %= screen_width
                ship_y_offset2 %= screen_height
            else:
                current_image_2 = ship_image1_1
                ship_side2 += spin_speed

            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, '#b8860b', (1000, 1000), 270, 0)
            pygame.draw.circle(screen, '#b5800d', (1000, 1000), 270, 50)
            pygame.draw.circle(screen, '#b8860b', (0, 0), 270, 0)
            pygame.draw.circle(screen, '#b5800d', (0, 0), 270, 50)

            rotated_ship = pygame.transform.rotate(current_image, ship_side)
            x = ship.centerx + ship_x_offset
            y = ship.centery + ship_y_offset
            x_draw = x % screen_width
            y_draw = y % screen_height
            if x < 0:
                x_draw += screen_width
            if y < 0:
                y_draw += screen_height
            rotated_rect = rotated_ship.get_rect(center=(x_draw, y_draw))
            screen.blit(rotated_ship, rotated_rect)

            rotated_ship2 = pygame.transform.rotate(current_image_2, ship_side2)
            x2 = ship2.centerx + ship_x_offset2
            y2 = ship2.centery + ship_y_offset2
            x_draw2 = x2 % screen_width
            y_draw2 = y2 % screen_height
            if x2 < 0:
                x_draw2 += screen_width
            if y2 < 0:
                y_draw2 += screen_height
            rotated_rect2 = rotated_ship2.get_rect(center=(x_draw2, y_draw2))
            screen.blit(rotated_ship2, rotated_rect2)

            pygame.display.flip()


    game_process()
    pygame.quit()