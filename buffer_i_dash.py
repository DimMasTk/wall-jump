import pygame

# Константы
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 120
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Определение класса Player
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.acceleration_y = 0.4
        self.jump_power = -12
        self.max_speed_x = 5
        self.max_speed_y = 12
        self.jumping = False
        self.on_ground = False
        self.boost_count = 1
        self.dash_cooldown = 0
        self.last_move_direction = 'right'
        self.on_wall = False
        self.yvel = 0
        self.wall_jump_height_multiplier = 0.5  # Изменение множителя высоты прыжка от стены
        self.wall_jump_pushback_speed = 20  # Устанавливаем скорость отталкивания от стены
        self.wall_jump_climb_speed = -2  # Устанавливаем скорость поднятия по стене

    def update(self, keys, platforms, green_thing):
        self.speed_y = min(self.speed_y + self.acceleration_y, self.max_speed_y)

        if keys[pygame.K_a]:
            self.speed_x = max(self.speed_x - 0.5, -self.max_speed_x)
            self.last_move_direction = 'left'
        elif keys[pygame.K_d]:
            self.speed_x = min(self.speed_x + 0.5, self.max_speed_x)
            self.last_move_direction = 'right'
        else:
            self.speed_x *= 0.9

        if keys[pygame.K_SPACE] and (self.on_ground or self.boost_count > 0):
            self.speed_y = self.jump_power
            self.jumping = True
            self.on_ground = False
            if self.boost_count > 0:
                self.boost_count -= 1

        if keys[pygame.K_LSHIFT] and self.dash_cooldown <= 0:
            dash_speed = 20 if self.last_move_direction == 'right' else -20
            self.speed_x = dash_speed
            self.dash_cooldown = 60
            self.speed_y = 0

        self.rect.x += self.speed_x
        self.handle_collisions_x(platforms)

        self.rect.y += self.speed_y + self.yvel

        self.handle_collisions_y(platforms)

        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0

        if pygame.sprite.collide_rect(self, green_thing):
            green_thing.handle_collision(self)

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def handle_collisions_x(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                if self.speed_x > 0:
                    self.rect.right = sprite.rect.left
                elif self.speed_x < 0:
                    self.rect.left = sprite.rect.right
                if sprite.is_vertical_platform:
                    self.on_wall = True
                    if self.speed_x != 0:
                        self.boost_count = 1  # Восстанавливаем буфер прыжков при контакте со стеной

    def handle_collisions_y(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                if self.speed_y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.speed_y = 0
                    self.on_ground = True
                elif self.speed_y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.speed_y = 0
                    if sprite.is_vertical_platform and pygame.key.get_pressed()[pygame.K_SPACE]:
                        self.on_wall = True
                        self.speed_y = self.jump_power * self.wall_jump_height_multiplier
                        self.jumping = True
                        self.boost_count -= 1
                        self.speed_x = -self.wall_jump_pushback_speed if self.speed_x > 0 else self.wall_jump_pushback_speed
                if sprite.is_vertical_platform:
                    self.yvel = 0
                    if self.rect.bottom > sprite.rect.top and pygame.key.get_pressed()[pygame.K_SPACE]:
                        self.on_wall = True
                        self.speed_y = self.wall_jump_climb_speed  # Используем скорость поднятия по стене
                        self.jumping = True
                        self.boost_count -= 1
                        self.speed_x = -self.wall_jump_pushback_speed if self.speed_x > 0 else self.wall_jump_pushback_speed
                    else:
                        self.yvel = 3


# Определение класса Platform
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_vertical=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_vertical_platform = is_vertical


# Определение класса GreenThing
class GreenThing(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def handle_collision(self, player):
        print("Player collided with the Green Thing!")
        player.boost_count += 1


def main():
    pygame.init()

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("My Game")

    all_sprites_list = pygame.sprite.Group()
    platform_list = pygame.sprite.Group()

    player = Player(0, SCREEN_HEIGHT - 100)
    all_sprites_list.add(player)

    platform = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
    all_sprites_list.add(platform)
    platform_list.add(platform)

    platform = Platform(500, SCREEN_HEIGHT - 100, 300, 20)
    all_sprites_list.add(platform)
    platform_list.add(platform)

    platform = Platform(900, SCREEN_HEIGHT - 200, 300, 20)
    all_sprites_list.add(platform)
    platform_list.add(platform)

    platform = Platform(1300, SCREEN_HEIGHT - 300, 300, 20)
    all_sprites_list.add(platform)
    platform_list.add(platform)

    vertical_platform = Platform(1000, 0, 20, SCREEN_HEIGHT, is_vertical=True)
    all_sprites_list.add(vertical_platform)
    platform_list.add(vertical_platform)

    green_thing = GreenThing(1650, 580, 50, 50)
    all_sprites_list.add(green_thing)

    clock = pygame.time.Clock()
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        keys = pygame.key.get_pressed()
        player.update(keys, platform_list, green_thing)

        screen.fill(WHITE)

        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
