import pygame
import json


pygame.init()
width = 800
height = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Моя игра')
clock = pygame.time.Clock()
fps = 60
level = 5
max_level = 5
def reset_level():
    player.rect.x = 60
    player.rect.y = 600
    lava_group.empty()
    exit_group.empty()
    key_group.empty()
    with open(f'levels/level{level}.json', 'r') as file:
        world_data = json.load(file)
    world = World(world_data)
    return world
tile_size = 40
game_over = 0

bg = pygame.image.load('images/bg7.png')


class Player:
    def __init__(self):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        for num in range(1, 3):
            img_right = pygame.image.load(f'images/player{num}.png')
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect(x=60, y=560)
        self.gravity = 0
        self.jumped = False
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.privid = pygame.image.load('images/images.png')
        self.privid = pygame.transform.scale(self.privid, (self.width, self.height))
        self.key = False

    def update(self):
        global game_over
        x = 0
        y = 0
        walk_speed = 10
        screen.blit(self.image, self.rect)
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_d]:
                x += 3
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a]:
                x -= 3
                self.counter += 1
                self.direction = -1
            if key[pygame.K_SPACE] and self.jumped == False:
                self.gravity = -18
                self.jumped = True

            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x , self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.jumped = False
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            elif pygame.sprite.spritecollide(self, exit_group, False) and self.key:
                game_over = 1
                self.key = False
            elif pygame.sprite.spritecollide(self, key_group, True):
                self.key = True


            self.rect.x += x
            self.rect.y += y

            if self.rect.bottom > height:
                self.rect.bottom = height
                self.jumped = False
        elif game_over == -1:
            self.image = self.privid
            if self.rect.y > 0:
                self.rect.y -= 3





class World:
    def __init__(self, data):
        self.tile_list = []
        dirt_img = pygame.image.load('images/map/tile10.png')
        snow_img = pygame.image.load('images/map/tile8.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1:dirt_img, 2:snow_img}
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    lava = Lava(col_count*tile_size, row_count*tile_size + (tile_size // 2))
                    lava_group.add(lava)
                elif tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                elif tile == 4:
                    key = Key(col_count * tile_size + (tile_size // 4), row_count * tile_size + (tile_size // 4))
                    key_group.add((key))
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/tile6.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

lava_group = pygame.sprite.Group()


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/door1.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

exit_group = pygame.sprite.Group()

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('images/map/key4.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

key_group = pygame.sprite.Group()


class Button():
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center= (x, y))

    def draw(self):
        screen.blit(self.image, self.rect)
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        return action


restart_button = Button(width // 2, height // 2, 'images/buttons/restart_btn 2.png')
start_button = Button(width // 2 - 150, height // 2, 'images/buttons/start_btn 2.png')
exit_button = Button(width // 2 + 150, height // 2, 'images/buttons/exit_btn 2.png')


player = Player()
world = reset_level()

main_menu=True
run=True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    if main_menu:
        if exit_button.draw():
            run=False
        if start_button.draw():
            main_menu=False
    else:
        player.update()
        world.draw()
        lava_group.draw(screen)
        lava_group.update()
        exit_group.draw(screen)
        exit_group.update()
        key_group.draw(screen)
        key_group.update()
        if game_over == -1:
            if restart_button.draw():
                player = Player()
                world = reset_level()
                game_over = 0
        if game_over == 1:
            game_over = 0
            if level < max_level:
                level += 1
                world = reset_level()
            else:
                print('Win')
                main_menu = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
    pygame.display.update()

pygame.quit()

# создать 2 уровня (level2.json, level3.json)