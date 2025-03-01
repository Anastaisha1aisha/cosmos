import pygame
import math
import time
import random

def distance_point_to_segment(point, seg_start, seg_end):
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)

class Bullet:
    def __init__(self, x, y, angle, speed, shooter, damage=25):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed * 0.75
        self.shooter = shooter
        self.dx = math.cos(math.radians(angle)) * self.speed
        self.dy = -math.sin(math.radians(angle)) * self.speed
        self.damage = damage

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 15)

class Mine:
    def __init__(self, x, y, shooter):
        self.x = x
        self.y = y
        self.shooter = shooter

    def draw(self, screen):
        pygame.draw.circle(screen, (128, 128, 128), (int(self.x), int(self.y)), 30)

class PowerUp:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.ptype = ptype
        self.pulse_scale = 1.0
        self.pulse_speed = 0.01

    def draw(self, screen):
        colors = {"laser": (255, 0, 0), "bullets": (255, 255, 0), "mine": (128, 128, 128), "forward": (0, 255, 0)}
        self.pulse_scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * self.pulse_speed)
        radius = int(22 * self.pulse_scale)
        pygame.draw.circle(screen, colors[self.ptype], (int(self.x), int(self.y)), radius)

class Ship:
    def __init__(self, image, pos, accelerate_key, fire_key):
        self.images = [image]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=pos)
        self.angle = 0
        self.skorost_x = 0
        self.skorost_y = 0
        self.rotation_speed = 2
        self.acceleration = 0.2
        self.friction = 0.98
        self.accelerate_key = accelerate_key
        self.fire_key = fire_key
        self.current_weapon = None
        self.health = 100
        self.last_fire_time = time.time()
        self.weapon_cooldown = 0.5
        self.laser_active = False
        self.laser_end_time = 0
        self.max_speed = 10
        self.forward_active = False
        self.forward_end_time = 0
        self.last_forward_fire_time = 0

    def switch_image(self, moving):
        if moving:
            self.image_index = (self.image_index + 1) % len(self.images)
        else:
            self.image_index = 0
        self.image = self.images[self.image_index]

    def update(self, keys, screen_width, screen_height):
        moving = False
        if keys[self.accelerate_key]:
            ax = math.cos(math.radians(self.angle)) * self.acceleration
            ay = -math.sin(math.radians(self.angle)) * self.acceleration
            self.skorost_x += ax
            self.skorost_y += ay
            moving = True
        else:
            self.skorost_x *= self.friction
            self.skorost_y *= self.friction
            self.angle -= self.rotation_speed

        speed = math.hypot(self.skorost_x, self.skorost_y)
        if speed > self.max_speed:
            factor = self.max_speed / speed
            self.skorost_x *= factor
            self.skorost_y *= factor

        self.switch_image(moving)
        new_x = (self.rect.centerx + self.skorost_x) % screen_width
        new_y = (self.rect.centery + self.skorost_y) % screen_height
        self.rect.center = (new_x, new_y)

    def get_nose(self):
        offset = 60
        nose_x = self.rect.centerx + offset * math.cos(math.radians(self.angle))
        nose_y = self.rect.centery - offset * math.sin(math.radians(self.angle))
        return (nose_x, nose_y)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect)

    def draw_health_line(self, screen):
        bar_width = 100
        bar_height = 10
        fill = (self.health / 100) * bar_width
        x, y = self.rect.center
        outline_rect = pygame.Rect(x - bar_width // 2, y - 80, bar_width, bar_height)
        fill_rect = pygame.Rect(x - bar_width // 2, y - 80, fill, bar_height)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)

wins1 = 0
wins2 = 0
round_number = 1

class GameProcess:
    def __init__(self, screen_width, screen_height, ship_image1, ship_image2, ship_images1, ship_images2):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ship1 = Ship(ship_image1, (self.screen_width // 3, self.screen_height // 2), pygame.K_SPACE, pygame.K_f)
        self.ship2 = Ship(ship_image2, (2 * self.screen_width // 3, self.screen_height // 2), pygame.K_RETURN, pygame.K_g)
        self.ship1.images = ship_images1
        self.ship2.images = ship_images2
        self.bullets = []
        self.mines = []
        self.powerups = []
        self.last_powerup_time = time.time()
        self.powerup_interval = 5

    def spawn_powerup(self):
        if len(self.powerups) < 3:
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(50, self.screen_height - 50)
            ptype = random.choice(["laser", "bullets", "mine", "forward"])
            powerup = PowerUp(x, y, ptype)
            self.powerups.append(powerup)

    def check_powerup_collision(self, ship):
        for powerup in self.powerups[:]:
            dist = math.hypot(ship.rect.centerx - powerup.x, ship.rect.centery - powerup.y)
            if dist < 50:
                if powerup.ptype == "laser":
                    ship.laser_active = True
                    ship.laser_end_time = time.time() + 3
                    ship.current_weapon = "laser"
                elif powerup.ptype == "bullets":
                    ship.current_weapon = "bullets"
                    self.fire_weapon(ship)
                elif powerup.ptype == "mine":
                    ship.current_weapon = "mine"
                    self.fire_weapon(ship)
                elif powerup.ptype == "forward":
                    ship.forward_active = True
                    ship.forward_end_time = time.time() + 2
                    ship.last_forward_fire_time = 0
                    ship.current_weapon = "forward"
                self.powerups.remove(powerup)
                ship.last_fire_time = time.time()

    def fire_weapon(self, ship):
        if time.time() - ship.last_fire_time < ship.weapon_cooldown:
            return
        if ship.current_weapon == "bullets":
            for angle in range(0, 360, 45):
                nose = ship.get_nose()
                b = Bullet(nose[0], nose[1], angle, 10, ship, damage=25)
                self.bullets.append(b)
        elif ship.current_weapon == "mine":
            m = Mine(ship.rect.centerx, ship.rect.centery, ship)
            self.mines.append(m)
        ship.current_weapon = None
        ship.last_fire_time = time.time()

    def update_forward_weapon(self, ship):
        if ship.forward_active:
            current_time = time.time()
            if current_time - ship.last_forward_fire_time >= 0.33:
                nose = ship.get_nose()
                b = Bullet(nose[0], nose[1], ship.angle, 10, ship, damage=20)
                self.bullets.append(b)
                ship.last_forward_fire_time = current_time
            if current_time > ship.forward_end_time:
                ship.forward_active = False
                ship.current_weapon = None

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if (bullet.x < 0 or bullet.x > self.screen_width or
                bullet.y < 0 or bullet.y > self.screen_height):
                self.bullets.remove(bullet)
                continue
            if bullet.shooter == self.ship1:
                if self.check_collision(bullet, self.ship2):
                    self.ship2.health -= bullet.damage
                    self.bullets.remove(bullet)
            elif bullet.shooter == self.ship2:
                if self.check_collision(bullet, self.ship1):
                    self.ship1.health -= bullet.damage
                    self.bullets.remove(bullet)

    def update_mines(self):
        for mine in self.mines[:]:
            if mine.shooter == self.ship1:
                if self.check_mine_collision(mine, self.ship2):
                    self.ship2.health -= 50
                    self.mines.remove(mine)
            elif mine.shooter == self.ship2:
                if self.check_mine_collision(mine, self.ship1):
                    self.ship1.health -= 50
                    self.mines.remove(mine)

    def update_laser(self, ship, enemy, screen):
        if ship.laser_active:
            nose = ship.get_nose()
            end = (nose[0] + 200 * math.cos(math.radians(ship.angle)),
                   nose[1] - 200 * math.sin(math.radians(ship.angle)))
            pygame.draw.line(screen, (255, 255, 255), nose, end, 7)
            pygame.draw.line(screen, (255, 0, 0), nose, end, 5)
            dist = distance_point_to_segment(enemy.rect.center, nose, end)
            if dist < 36:
                enemy.health -= 10
            if time.time() > ship.laser_end_time:
                ship.laser_active = False
                ship.current_weapon = None

    def check_collision(self, bullet, ship):
        return math.hypot(bullet.x - ship.rect.centerx, bullet.y - ship.rect.centery) < 36

    def check_mine_collision(self, mine, ship):
        return math.hypot(mine.x - ship.rect.centerx, mine.y - ship.rect.centery) < 48

    def check_ship_collision(self):
        dx = self.ship2.rect.centerx - self.ship1.rect.centerx
        dy = self.ship2.rect.centery - self.ship1.rect.centery
        distance = math.hypot(dx, dy)
        min_distance = (self.ship1.rect.width + self.ship2.rect.width) / 4 * 1.2
        if distance < min_distance:
            overlap = min_distance - distance
            if distance == 0:
                dx, dy = 1, 0
            else:
                dx, dy = dx / distance, dy / distance
            self.ship1.rect.centerx -= dx * overlap / 2
            self.ship1.rect.centery -= dy * overlap / 2
            self.ship2.rect.centerx += dx * overlap / 2
            self.ship2.rect.centery += dy * overlap / 2

    def update(self, screen):
        global wins1, wins2, round_number
        keys = pygame.key.get_pressed()

        if wins1 == 3 or wins2 == 3:
            return

        if self.ship1.health <= 0 or self.ship2.health <= 0:
            if self.ship1.health <= 0 and self.ship2.health > 0:
                wins2 += 1
            elif self.ship2.health <= 0 and self.ship1.health > 0:
                wins1 += 1
            round_number += 1

            if wins1 < 3 and wins2 < 3:
                self.__init__(self.screen_width, self.screen_height,
                              self.ship1.image, self.ship2.image,
                              self.ship1.images, self.ship2.images)
            return

        self.ship1.update(keys, self.screen_width, self.screen_height)
        self.ship2.update(keys, self.screen_width, self.screen_height)
        self.check_ship_collision()
        self.check_powerup_collision(self.ship1)
        self.check_powerup_collision(self.ship2)
        self.update_laser(self.ship1, self.ship2, screen)
        self.update_laser(self.ship2, self.ship1, screen)
        self.update_forward_weapon(self.ship1)
        self.update_forward_weapon(self.ship2)
        self.update_bullets()
        self.update_mines()
        if time.time() - self.last_powerup_time >= self.powerup_interval:
            self.spawn_powerup()
            self.last_powerup_time = time.time()

    def draw(self, screen):
        for powerup in self.powerups:
            powerup.draw(screen)
        for mine in self.mines:
            mine.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        self.ship1.draw(screen)
        self.ship1.draw_health_line(screen)
        self.ship2.draw(screen)
        self.ship2.draw_health_line(screen)

        font = pygame.font.Font(None, 36)
        round_text = font.render(f"ROUND {round_number}", True, (255, 255, 255))
        round_rect = round_text.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(round_text, round_rect)

        wins1_text = font.render(f"PLAYER 1: {wins1}", True, (255, 255, 255))
        screen.blit(wins1_text, (10, 10))
        wins2_text = font.render(f"PLAYER 2: {wins2}", True, (255, 255, 255))
        wins2_rect = wins2_text.get_rect(topright=(self.screen_width - 10, 10))
        screen.blit(wins2_text, wins2_rect)

        button_back = pygame.Rect(self.screen_width // 2 - 40, 10, 75, 25)
        pygame.draw.rect(screen, (200, 200, 200), button_back)
        font = pygame.font.Font(None, 24)
        text_back = font.render("Назад", True, (0, 0, 0))
        screen.blit(text_back, (self.screen_width // 2 - 28, 15))

        if wins1 == 3 or wins2 == 3:
            winner = "PLAYER 1" if wins1 == 3 else "PLAYER 2"
            win_text = pygame.font.Font(None, 72).render(f"{winner} WIN", True, (255, 255, 255))
            win_rect = win_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(win_text, win_rect)

        if self.ship1.health <= 0 or self.ship2.health <= 0:
            button_menu = pygame.Rect(self.screen_width // 2 - 50, self.screen_height // 2 + 100, 100, 50)
            pygame.draw.rect(screen, (200, 200, 200), button_menu)
            font = pygame.font.Font(None, 36)
            text_menu = font.render("Меню", True, (0, 0, 0))
            screen.blit(text_menu, (self.screen_width // 2 - 40, self.screen_height // 2 + 115))

pygame.init()
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Космос")

ship_images = {"Корабль_1": [pygame.image.load(f"Корабль_{i}.png").convert_alpha() for i in range(1, 4)],
               "Корабль_1_1": [pygame.image.load(f"Корабль_{i}_1.png").convert_alpha() for i in range(1, 4)],
               "Корабль_1_2": [pygame.image.load(f"Корабль_{i}_2.png").convert_alpha() for i in range(1, 4)],
               "Корабль_1_3": [pygame.image.load(f"Корабль_{i}_3.png").convert_alpha() for i in range(1, 4)],
               "Корабль_1_4": [pygame.image.load(f"Корабль_{i}_4.png").convert_alpha() for i in range(1, 4)]}

ship_size = (150, 100)
for key in ship_images:
    for i in range(len(ship_images[key])):
        ship_images[key][i] = pygame.transform.scale(ship_images[key][i], ship_size)

stars = [[random.randint(0, screen_width), random.randint(0, screen_height),
          random.choice([1, 2, 3]), random.randint(0, 255)] for i in range(100)]

def draw_stars():
    for star in stars:
        bright = star[3]
        pygame.draw.circle(screen, (bright, bright, bright), (star[0], star[1]), 2)

def new_stars():
    for star in stars:
        star[0] -= star[2] * 0.5
        if star[0] < 0:
            star[0] = screen_width
            star[1] = random.randint(0, screen_height)
        star[3] += random.choice([-10, 10])
        if star[3] < 0:
            star[3] = 0
        elif star[3] > 255:
            star[3] = 255

selected_design_player1 = "Корабль_1"
selected_design_player2 = "Корабль_1_1"

def game_process():
    global selected_design_player1, selected_design_player2, wins1, wins2, round_number

    ship_images_player1 = ship_images[selected_design_player1]
    ship_images_player2 = ship_images[selected_design_player2]

    game = GameProcess(screen_width, screen_height,
                       ship_images_player1[0], ship_images_player2[0],
                       ship_images_player1, ship_images_player2)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if game.ship1.health <= 0 or game.ship2.health <= 0:
                    button_menu = pygame.Rect(screen_width // 2 - 50, screen_height // 2 + 100, 100, 50)
                    if button_menu.collidepoint(mouse_pos):
                        wins1 = 0
                        wins2 = 0
                        round_number = 1
                        return
                button_back = pygame.Rect(460, 10, 75, 25)
                if button_back.collidepoint(mouse_pos):
                    return

        screen.fill((0, 0, 0))
        draw_stars()

        game.update(screen)
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def draw_design_choice():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 50)
    text_player1 = font.render("Игрок 1", True, (255, 255, 255))
    text_player2 = font.render("Игрок 2", True, (255, 255, 255))
    screen.blit(text_player1, (160, 50))
    screen.blit(text_player2, (700, 50))
    for i, key in enumerate(ship_images.keys()):
        screen.blit(ship_images[key][0], (140, 100 + i * 120))
        if key == selected_design_player1:
            pygame.draw.rect(screen, (0, 200, 150), (150, 90 + i * 120, ship_size[0] + 20, ship_size[1] + 20), 3)
    for i, key in enumerate(ship_images.keys()):
        screen.blit(ship_images[key][0], (680, 100 + i * 120))
        if key == selected_design_player2:
            pygame.draw.rect(screen, (0, 200, 150), (690, 90 + i * 120, ship_size[0] + 20, ship_size[1] + 20), 3)
    back_button = pygame.Rect(300, 800, 400, 60)
    pygame.draw.rect(screen, (0, 100, 100), back_button)
    font = pygame.font.Font(None, 70)
    back_text = font.render("Выбрать дизайн", True, (255, 255, 255))
    screen.blit(back_text, (300, 810))

def design_selection():
    global selected_design_player1, selected_design_player2
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 300 <= mouse_pos[0] <= 700 and 800 <= mouse_pos[1] <= 860:
                    return
                for i, key in enumerate(ship_images.keys()):
                    if (140 <= mouse_pos[0] <= 140 + ship_size[0] and
                        100 + i * 120 <= mouse_pos[1] <= 100 + i * 120 + ship_size[1]):
                        selected_design_player1 = key
                for i, key in enumerate(ship_images.keys()):
                    if (680 <= mouse_pos[0] <= 680 + ship_size[0] and
                        100 + i * 120 <= mouse_pos[1] <= 100 + i * 120 + ship_size[1]):
                        selected_design_player2 = key
        draw_design_choice()
        pygame.display.flip()

def menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(pygame.mouse.get_pos()):
                    game_process()
                if button_design.collidepoint(pygame.mouse.get_pos()):
                    design_selection()

        new_stars()
        screen.fill((0, 0, 0))
        draw_stars()

        font = pygame.font.Font(None, 74)

        ship_rect = ship_images["Корабль_1"][0].get_rect(center=(screen_width // 2 - 10, screen_height // 2 - 50))
        screen.blit(ship_images["Корабль_1"][0], ship_rect)

        button_play = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 30, 200, 70)
        pygame.draw.rect(screen, (122, 66, 195), button_play)
        text_play = font.render("Играть", True, (0, 0, 0))
        text_rect_pl = text_play.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
        screen.blit(text_play, text_rect_pl)

        button_design = pygame.Rect(screen_width // 2 - 225, screen_height // 2 + 150, 450, 50)
        pygame.draw.rect(screen, (200, 66, 195), button_design)
        text_design = font.render("Выбрать дизайн", True, (0, 0, 0))
        text_rect_design = text_design.get_rect(center=(screen_width // 2, screen_height // 2 + 180))
        screen.blit(text_design, text_rect_design)

        question_mark = pygame.Rect(screen_width - 50, 10, 40, 40)
        pygame.draw.circle(screen, (255, 255, 255), (screen_width - 30, 30), 20)
        font_inf= pygame.font.Font(None, 36)
        text_inf = font_inf.render("?", True, (0, 0, 0))
        screen.blit(text_inf, (screen_width - 37, 20))

        mouse_pos = pygame.mouse.get_pos()
        if question_mark.collidepoint(mouse_pos):
            info_box = pygame.Rect(screen_width - 450, 50, 400, 200)
            pygame.draw.rect(screen, (200, 200, 200), info_box)
            font_info = pygame.font.Font(None, 34)
            text_info1 = font_info.render("Управление:", True, (0, 0, 0))
            text_info2 = font_info.render("Игрок 1: Пробел - движение", True, (0, 0, 0))
            text_info3 = font_info.render("Игрок 2: Enter - движение", True, (0, 0, 0))
            text_info4 = font_info.render("Цель игры:", True, (0, 0, 0))
            text_info5 = font_info.render("победить другого игрока 3 раза", True, (0, 0, 0))
            screen.blit(text_info1, (screen_width - 440, 70))
            screen.blit(text_info2, (screen_width - 440, 100))
            screen.blit(text_info3, (screen_width - 440, 130))
            screen.blit(text_info4, (screen_width - 440, 170))
            screen.blit(text_info5, (screen_width - 440, 200))

        pygame.display.flip()

menu()
pygame.quit()