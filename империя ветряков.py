import pygame
import sys
import time
import random
import math

pygame.init()
pygame.mixer.init()

# Окно
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Империя Ветряков")

# Цвета
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (50, 180, 50)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
DARK_GREEN = (34, 139, 34)
RUST = (170, 120, 80)
SKIN = (255, 220, 177)
RED = (200, 0, 0)
GOLD = (255, 215, 0)
DIAMOND = (180, 255, 255)

font = pygame.font.SysFont("Arial", 28, bold=True)
font_small = pygame.font.SysFont("Arial", 22)
font_msg = pygame.font.SysFont("Arial", 26, bold=True)

# Игровые параметры
money = 0
people_helped = 0
message_text = ""
message_timer = 0

def show_message(text, duration=2):
    global message_text, message_timer
    message_text = text
    message_timer = time.time() + duration

# Фон
trees = [(random.randint(0, WIDTH), HEIGHT - 150, random.randint(80, 150)) for _ in range(10)]
grass = [(random.randint(0, WIDTH), random.randint(HEIGHT - 60, HEIGHT - 30), random.randint(10, 25)) for _ in range(200)]

# Класс ветряка
class Windmill:
    def __init__(self, x, base_income=3, help_reward=5):
        self.level = 1
        self.income = base_income
        self.help_reward = help_reward
        self.help_interval = 10
        self.last_help_time = time.time()
        self.last_income_time = time.time()
        self.width = 30
        self.height = 300
        self.rect = pygame.Rect(x, HEIGHT - 100 - self.height, self.width, self.height)
        self.angle = 0
        self.upgrade_cost = 20
        self.unlocked = True

    def get_colors(self):
        if self.level <= 3:
            return (RUST, RUST)
        elif self.level == 4:
            return (WHITE, BLACK)
        elif self.level <= 6:
            return (BLACK, BLACK)
        elif self.level <= 9:
            return (GOLD, GOLD)
        else:
            return (DIAMOND, DIAMOND)

    def draw(self):
        tower_color, blade_color = self.get_colors()
        pygame.draw.rect(screen, tower_color, self.rect)
        center = (self.rect.centerx, self.rect.top + 60)
        self.angle += 2
        for a in [0, 90, 180, 270]:
            end_x = center[0] + 70 * pygame.math.Vector2(1, 0).rotate(self.angle + a).x
            end_y = center[1] + 70 * pygame.math.Vector2(1, 0).rotate(self.angle + a).y
            pygame.draw.line(screen, blade_color, center, (end_x, end_y), 10)

    def update_income(self):
        global money
        now = time.time()
        if now - self.last_income_time >= 2:
            money += self.income
            self.last_income_time = now

    def update_help(self):
        global money, people_helped
        now = time.time()
        if now - self.last_help_time >= self.help_interval:
            money += self.help_reward
            people_helped += 1
            self.last_help_time = now

    def upgrade(self, multiplier_cost=1):
        global money
        cost = int(self.upgrade_cost * multiplier_cost)
        if money >= cost:
            money -= cost
            self.level += 1
            self.income *= 2
            self.help_reward *= 2
            self.help_interval = max(2, self.help_interval / 2)
            if self.level == 2:
                self.upgrade_cost = 320
            elif self.level == 3:
                self.upgrade_cost = 600
            else:
                self.upgrade_cost = int(self.upgrade_cost * 2.5)
            show_message("Улучшено!")
        else:
            show_message("Вам не хватает денег!")

# Первый ветряк
windmill1 = Windmill(WIDTH//2 - 150)
# Второй ветряк
windmill2 = Windmill(WIDTH//2 + 150)
windmill2.unlocked = False
windmill2.upgrade_cost *= 5  # 5 раз дороже

# Замок второго ветряка
lock_rect = pygame.Rect(windmill2.rect.x - 10, windmill2.rect.y + 50, 80, 100)

# Окна
show_upgrade_window = False
show_second_window = False
selected_windmill = None

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 100, WIDTH, 100))
    for x, y, h in trees:
        pygame.draw.rect(screen, BROWN, (x, y, 15, h))
        pygame.draw.circle(screen, DARK_GREEN, (x + 7, y - 10), h // 3)
    for x, y, h in grass:
        pygame.draw.line(screen, DARK_GREEN, (x, y), (x, y - h), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Улучшение
            if show_upgrade_window and selected_windmill:
                yes_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 30, 90, 45)
                no_rect = pygame.Rect(WIDTH//2 + 40, HEIGHT//2 + 30, 90, 45)
                if yes_rect.collidepoint(mouse_pos):
                    multiplier = 5 if selected_windmill == windmill2 else 1
                    selected_windmill.upgrade(multiplier)
                    show_upgrade_window = False
                elif no_rect.collidepoint(mouse_pos):
                    show_upgrade_window = False

            # Покупка второго
            elif show_second_window:
                yes_rect = pygame.Rect(lock_rect.x - 20, lock_rect.y + 110, 90, 45)
                no_rect = pygame.Rect(lock_rect.x + 60, lock_rect.y + 110, 90, 45)
                if yes_rect.collidepoint(mouse_pos):
                    if money >= 5000:
                        money -= 5000
                        windmill2.unlocked = True
                        show_message("Второй ветряк куплен!")
                    else:
                        show_message("Вам не хватает денег!")
                    show_second_window = False
                elif no_rect.collidepoint(mouse_pos):
                    show_second_window = False

            # Клик по ветрякам
            elif windmill1.rect.collidepoint(mouse_pos) and windmill1.unlocked:
                selected_windmill = windmill1
                show_upgrade_window = True
            elif windmill2.rect.collidepoint(mouse_pos):
                if windmill2.unlocked:
                    selected_windmill = windmill2
                    show_upgrade_window = True
                elif windmill1.level >= 5:
                    show_second_window = True

            # Клик по замку второго
            elif not windmill2.unlocked and windmill1.level >= 5 and lock_rect.collidepoint(mouse_pos):
                show_second_window = True

    # Обновление дохода и помощи
    windmill1.update_income()
    windmill1.update_help()
    if windmill2.unlocked:
        windmill2.update_income()
        windmill2.update_help()

    # Отрисовка ветряков
    windmill1.draw()
    if windmill2.unlocked:
        windmill2.draw()

    # Замок
    if not windmill2.unlocked and windmill1.level >= 5:
        pygame.draw.rect(screen, BLACK, lock_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, (lock_rect.x + 15, lock_rect.y - 20, 50, 30), border_radius=15)
        pygame.draw.rect(screen, GOLD, (lock_rect.x + 25, lock_rect.y + 40, 30, 40), border_radius=5)
        screen.blit(font_small.render("🔒", True, GOLD), (lock_rect.x + 28, lock_rect.y + 45))

    # Текст
    screen.blit(font.render(f"Деньги: {int(money)} BYN", True, BLACK), (20, 20))
    screen.blit(font.render(f"Помог: {people_helped}", True, BLACK), (250, 60))
    screen.blit(font.render(f"Уровень 1: {windmill1.level}/10", True, BLACK), (20, 100))
    lvl2_text = f"{windmill2.level}/10" if windmill2.unlocked else "Закрыт"
    screen.blit(font.render(f"Уровень 2: {lvl2_text}", True, BLACK), (250, 100))

    # Сообщения
    if message_text and time.time() < message_timer:
        msg_surface = font_msg.render(message_text, True, RED)
        screen.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, 20))

    # Окно улучшения
    if show_upgrade_window and selected_windmill:
        w, h = 360, 180
        rect = pygame.Rect(WIDTH//2 - w//2, HEIGHT//2 - h//2, w, h)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 3)
        text1 = font_small.render(f"Улучшить ветряк до уровня {selected_windmill.level + 1}?", True, BLACK)
        cost = int(selected_windmill.upgrade_cost * (5 if selected_windmill == windmill2 else 1))
        text2 = font_small.render(f"Стоимость: {cost} BYN", True, RED)
        screen.blit(text1, (rect.x + 30, rect.y + 40))
        screen.blit(text2, (rect.x + 40, rect.y + 70))
        yes_rect = pygame.Rect(rect.x + 40, rect.y + 110, 90, 45)
        no_rect = pygame.Rect(rect.x + 180, rect.y + 110, 90, 45)
        pygame.draw.rect(screen, (0,200,0), yes_rect, border_radius=8)
        pygame.draw.rect(screen, (200,0,0), no_rect, border_radius=8)
        screen.blit(font_small.render("ДА", True, WHITE), (yes_rect.x+25, yes_rect.y+10))
        screen.blit(font_small.render("НЕТ", True, WHITE), (no_rect.x+25, no_rect.y+10))

    # Окно покупки второго ветряка
    if show_second_window:
        rect = pygame.Rect(lock_rect.x-40, lock_rect.y-40, 200, 150)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 3)
        screen.blit(font_small.render("Купить 2-й ветряк", True, BLACK), (rect.x + 20, rect.y + 15))
        screen.blit(font_small.render("за 5000 BYN?", True, RED), (rect.x + 20, rect.y + 45))
        yes_rect = pygame.Rect(rect.x+20, rect.y+90, 90,45)
        no_rect = pygame.Rect(rect.x+110, rect.y+90, 90,45)
        pygame.draw.rect(screen,(0,200,0), yes_rect, border_radius=8)
        pygame.draw.rect(screen,(200,0,0), no_rect, border_radius=8)
        screen.blit(font_small.render("ДА", True, WHITE), (yes_rect.x+25, yes_rect.y+10))
        screen.blit(font_small.render("НЕТ", True, WHITE), (no_rect.x+25, no_rect.y+10))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()

