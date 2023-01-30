import pygame
import math
import sys
import os
import random
cur_scene = None
x = 600
y = 350
menu_texts = ["To infinity and beyond!",
              "v 0.1",
              "How do you like this, Elon Musk?",
              "r2-d2",
              "Insufficient facts always invite danger",
              "Clown Wars",
              ]
particles = []
colors = [(255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255)]


# класс частиц
class Particle:
    def __init__(self, x, y, xvel, yvel, radius, color, gravity=None):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.radius = radius
        self.color = color
        self.gravity = gravity

    # метод отрисовки частицы
    def render(self, window):
        self.x += self.xvel
        self.y += self.yvel
        if self.gravity != None:
            self.yvel += self.gravity
        self.radius -= 0.05
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)


# отрисовка частиц на экране
def DrawParticles():
    for particle in particles:
        particle.render(screen)
        if particle.radius <= 0:
            particles.remove(particle)


# функция, вызываемая при подборе аптечки
def medicine_chest(object):
    object.change_health(3)


# функция, вызываемая при подборе бонуса x2
def x2(object):
    object.x2timer = 15


# загрузка изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# смена сцены
def switch_scene(scene, start_scene):
    global cur_scene
    cur_scene = scene
    start_scene()


# начало игры
def start_game():
    switch_scene(level, lvl1)
    ship.image = pygame.transform.scale(ship.image, (64, 64))


# класс текста "Win"
class Win(pygame.sprite.Sprite):
    image = pygame.image.load("data/win.png")

    def __init__(self):
        super().__init__(ui)
        self.timer = 0
        self.scale = 8
        self.is_increase = False
        self.frames = []
        self.cut_sheet(Win.image, 3, 3)
        self.cur_frame = 0
        self.image = self.frames[round(self.cur_frame)]
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(600, 170)

    # анимация рандомного текста
    def animate(self):
        # смена кадров
        self.timer += 1
        if self.timer == 90:
            self.timer = 0
        self.image = self.frames[self.timer // 10]
        self.orig_image = self.image

        # изменение размера
        if self.is_increase:
            self.scale += 0.01
        else:
            self.scale -= 0.01
        if self.scale <= 7.5:
            self.is_increase = True
        elif self.scale >= 8.5:
            self.is_increase = False
        self.image = pygame.transform.scale(self.orig_image, (56 * self.scale, 22 * self.scale))
        self.rect.x = 600 - 56 * self.scale / 2
        self.rect.y = 350 - 22 * self.scale / 2

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        pass


# класс портала
class Portal(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.timer = 5
        self.animation = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 8
        self.image = self.frames[round(self.cur_frame)]
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = pygame.Rect(x, y, 200, 200)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # анимация портала
    def animate(self):
        global lvls, lvl_id
        if self.timer == 0:
            self.timer = 5
            self.cur_frame += 1
            if self.animation == 0:
                # анимация появления
                if round(self.cur_frame) == 16:
                    self.animation = 1
                    self.cur_frame = 0
            elif self.animation == 1:
                # обычная анимация
                if round(self.cur_frame) == 8:
                    self.cur_frame = 0
            else:
                # анимация уничтожения и переход на следующий уровень
                if round(self.cur_frame) == 22:
                    if lvl_id != 3:
                        switch_scene(level, lvls[lvl_id + 1])
                    else:
                        switch_scene(win_scene, start_win)
                    self.kill()
            self.image = self.frames[round(self.cur_frame)]
            self.image = pygame.transform.scale(self.image, (256, 256))
        else:
            self.timer -= 1


# класс Астероида
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, radius, x, y, id):
        super().__init__(asteroids)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = id
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))
        self.original_image = self.image
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.radius = radius
        self.vx = random.randint(-1, 1)
        self.vy = random.randrange(-1, 1)
        self.data = ()

    def update(self):
        # передвижение астероида
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, asteroids):
            self.vy = -self.vy
            self.vx = -self.vx
            data = pygame.sprite.spritecollide(self, asteroids, False)
            for i in data:
                i.vy = -i.vy
                i.vx = -i.vx
        if pygame.sprite.spritecollideany(self, blocks):
            self.vy = -self.vy
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, objects):
            if random.randint(0, 10) == 0:
                Bonus(load_image("medicine_chest.png"), self.rect.x, self.rect.y, medicine_chest)
            self.kill()
            data = pygame.sprite.spritecollide(self, objects, False)
            for i in data:
                i.kill()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


# класс Пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, a, type):
        super().__init__(objects)
        global shoot
        shoot.play()
        self.lifetime = 100
        self.type = type
        self.a = a + random.randint(-5, 5)
        self.x = x
        self.y = y
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, self.a)
        self.rect = pygame.Rect(x - 70 * math.sin(self.a * math.pi / 180),
                                y - 70 * math.cos(self.a * math.pi / 180), *self.image.get_size())
        self.v = -10
        self.vx = 0
        self.vy = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # полёт пули
        if pygame.sprite.spritecollideany(self, blocks):
            self.kill()
        if self.lifetime == 0:
            self.kill()
        else:
            # анимация пули
            if self.lifetime == 90 or self.lifetime == 80:
                self.cur_frame += 1
                self.image = self.frames[self.cur_frame]
                self.image = pygame.transform.scale(self.image, tuple(map(lambda x: x * 10, self.image.get_size())))
                self.image = pygame.transform.rotate(self.original_image, self.a)

            self.lifetime -= 1
            self.vx = math.sin(self.a * math.pi / 180) * self.v
            self.vy = math.cos(self.a * math.pi / 180) * self.v
            self.rect = self.rect.move(self.vx, self.vy)


# класс Корабля
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.portal = None
        self.cd = 30
        self.protection_timer = 0
        self.fuel = 5
        self.health = 10
        self.x = x
        self.y = y
        self.max_v = 5
        self.image = load_image("blueship.png")
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.v = 0.1
        self.a = 0
        self.x2timer = 0
        self.forward = False
        self.down = False
        self.right = False
        self.left = False
        self.position = (self.x + 8, self.y + 8)

    # изменение здоровья
    def change_health(self, hp):
        self.health += hp
        if hp <= 0:
            self.protection_timer = 200

    def update(self, *args):
        self.x = self.rect.x
        self.y = self.rect.y
        if args[0].type == pygame.KEYDOWN:
            if args[0].key == 119:  #w
                self.forward = True
            if args[0].key == 115:  #s
                self.down = True
            if args[0].key == 97:   #d
                self.right = True
            if args[0].key == 100:  #a
                self.left = True
            if args[0].key == 32:   #space
                if self.cd == 0:
                    w, h = self.image.get_size()
                    if self.x2timer == 0:
                        bullet = Bullet(load_image("bullet.png"), 3, 1, self.x + 8, self.y + 8, self.a, 0)
                        objects.add(bullet)
                    else:
                        self.x2timer -= 1
                        bullet = Bullet(load_image("bullet.png"), 3, 1, self.x + 8, self.y + 8, self.a + 15, 0)
                        objects.add(bullet)
                        bullet = Bullet(load_image("bullet.png"), 3, 1, self.x + 8, self.y + 8, self.a - 15, 0)
                        objects.add(bullet)
                    self.v += 2
                    self.cd = 30
        if args[0].type == pygame.KEYUP:
            if args[0].key == 119:  #w
                self.forward = False
            if args[0].key == 115:  #s
                self.down = False
            if args[0].key == 100:  #a
                self.left = False
            if args[0].key == 97:   #d
                self.right = False

    # передвижение корабля
    def drive(self):
        if self.cd != 0:
            self.cd -= 1
        if pygame.sprite.spritecollideany(self, all_sprites):
            data = pygame.sprite.spritecollide(self, all_sprites, False)
            # телепортация
            if len(data) == 2 and self.portal != None:
                if self.portal in data:
                    if self.portal.animation == 1:
                        self.image.set_alpha(0)
                        self.portal.cur_frame = 16
                        self.portal.animation = 2
        if self.protection_timer == 0:
            self.image.set_alpha(255)
            if pygame.sprite.spritecollideany(self, asteroids):
                data = pygame.sprite.spritecollide(self, asteroids, False)
                for i in data:
                    i.kill()
                    self.change_health(-1)
                    if self.health < 0:
                        self.kill()
            if pygame.sprite.spritecollideany(self, objects):
                data = pygame.sprite.spritecollide(self, objects, False)
                for i in data:
                    if i.type == 1:
                        i.kill()
                        self.change_health(-1)
                        if self.health < 0:
                            self.kill()
            if pygame.sprite.spritecollideany(self, red_ships):
                # взрыв двух кораблей
                data = pygame.sprite.spritecollide(self, red_ships, False)
                for i in data:
                    i.kill()
                    boom.play()
                    self.change_health(-5)
                    self.v += 5
                    if self.health < 0:
                        self.kill()
        else:
            # защита
            t = self.protection_timer // 10
            if t % 2 == 0:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
            self.protection_timer -= 1
        # рассчёт скорости
        if self.forward:
            self.v -= 0.1
        elif self.v < 0:
            self.v += 0.1
        if self.down:
            self.v += 0.1
        elif self.v > 0:
            self.v -= 0.1
        # поворот
        if self.right:
            self.a += 2
            self.x = self.rect.x
            self.y = self.rect.y
            self.image = pygame.transform.rotate(self.original_image, self.a)
            self.rect = self.image.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
        if self.left:
            self.a -= 2
            self.x = self.rect.x
            self.y = self.rect.y
            self.image = pygame.transform.rotate(self.original_image, self.a)
            self.rect = self.image.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
        if abs(self.v) > self.max_v:
            self.v = self.max_v * (self.v / abs(self.v))
        # проекции на оси
        self.vx = math.sin(self.a * math.pi / 180) * self.v
        self.vy = math.cos(self.a * math.pi / 180) * self.v
        # проверка коллизий с блоками
        self.rect = self.rect.move(self.vx, 0)
        if pygame.sprite.spritecollideany(self, blocks):
            data = pygame.sprite.spritecollide(self, blocks, False)
            for i in data:
                self.rect = self.rect.move(-self.vx, 0)
                if self.protection_timer == 0:
                    if i.func != None:
                        i.func(self)
        self.rect = self.rect.move(0, self.vy)
        if pygame.sprite.spritecollideany(self, blocks):
            data = pygame.sprite.spritecollide(self, blocks, False)
            for i in data:
                self.rect = self.rect.move(0, -self.vy)
                if self.protection_timer == 0:
                    if i.func != None:
                        i.func(self)
        # просчёт границ
        if self.rect.y < 0:
            self.rect.y += 700
        if self.rect.y > 700:
            self.rect.y -= 700
        if self.rect.x < 0:
            self.rect.x += 1200
        if self.rect.x > 1200:
            self.rect.x -= 1200


# класс фона
class Background(pygame.sprite.Sprite):
    image = pygame.image.load("data/bg.jpg")

    def __init__(self):
        super().__init__(bg_objs)
        self.x = 0
        self.y = 0
        self.max_v = 1
        self.image = Background.image
        self.image = pygame.transform.scale(self.image, (2000, 1400))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(-500, -500)
        self.v = 0.02
        self.a = 0
        self.forward = False
        self.down = False
        self.right = False
        self.left = False

    # паралакс фона
    def paralax(self):
        self.rect.x = ship.rect.x // 10 - 500
        self.rect.y = ship.rect.y // 10 - 500

    def update(self, *args):
        pass


# класс вражеского корабля
class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.shoot_timer = 100
        super().__init__(red_ships)
        self.d = 0
        self.timer = 100
        self.fuel = 5
        self.health = 3
        self.x = x
        self.y = y
        self.max_v = 3
        self.image = load_image("ships/" + str(random.randint(1, 6)) + ".png")
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.original_image = self.image
        self.rect = self.rect.move(x, y)
        self.v = 4
        self.a = 0
        self.da = 0
        self.position = (self.x + 8, self.y + 8)

    def update(self):
        if self.shoot_timer == 0:
            # выстрел
            w, h = self.image.get_size()
            bullet = Bullet(load_image("enemy_bullet.png"), 3, 1, self.rect.x + 8,
                            self.rect.y + 8, self.a, 1)
            enemy_bullets.add(bullet)
            self.v += 2
            self.shoot_timer = random.randint(30, 300)
        else:
            self.shoot_timer -= 1
        if pygame.sprite.spritecollideany(self, blocks):
            data = pygame.sprite.spritecollide(self, blocks, False)
            for i in data:
                if i.func != None:
                    i.func(self)
        if pygame.sprite.spritecollideany(self, asteroids):
            data = pygame.sprite.spritecollide(self, asteroids, False)
            for i in data:
                i.kill()
                if abs(i.vx * i.vy * i.radius) > 0.5:
                    self.health -= 1
                    if self.health < 0:
                        self.kill()
        if pygame.sprite.spritecollideany(self, objects):
            data = pygame.sprite.spritecollide(self, objects, False)
            if self.timer == 0:
                for i in data:
                    if i.type == 0:
                        i.kill()
                        self.health -= 1
                        self.timer = 100
                        if self.health < 0:
                            self.kill()
        if self.timer == 0:
            self.image.set_alpha(255)
            # поворот к игроку
            self.d += random.uniform(-0.5, 0.5)
            x, y = ship.rect.x, ship.rect.y
            rel_x, rel_y = x - self.rect.x, y - self.rect.y
            self.a = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90 + self.d
            self.image = pygame.transform.rotate(self.original_image, int(self.a))
            sx, sy = self.rect.x, self.rect.y
            self.rect = self.image.get_rect(center=self.position)
            self.rect.x = sx
            self.rect.y = sy
            if abs(self.v) > self.max_v:
                self.v = self.max_v * (self.v / abs(self.v))
            # проекции на оси
            self.vx = math.sin(self.a) * self.v
            self.vy = math.cos(self.a) * self.v
            self.position = self.rect.x, self.rect.y
            self.rect = self.rect.move(self.vx, self.vy)
            # коллизия с блоками
            if pygame.sprite.spritecollideany(self, blocks):
                data = pygame.sprite.spritecollide(self, blocks, False)
                for i in data:
                    self.rect = self.rect.move(-self.vx, -self.vy)
        else:
            # защита
            t = self.timer // 10
            if t % 2 == 0:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
            self.timer -= 1


# класс барьера
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        self.image.set_alpha(0)


# класс логотипа в меню
class Logo(pygame.sprite.Sprite):
    image = pygame.image.load("data/logo.png")

    def __init__(self):
        super().__init__(ui)
        self.scale = 8
        self.is_increase = False
        self.image = Logo.image
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(600, 170)

    # анимация
    def animate(self):
        if self.is_increase:
            self.scale += 0.01
        else:
            self.scale -= 0.01
        if self.scale <= 7.5:
            self.is_increase = True
        elif self.scale >= 8.5:
            self.is_increase = False
        self.image = pygame.transform.scale(self.orig_image, (59 * self.scale, 35 * self.scale))
        self.rect.x = 600 - 59 * self.scale / 2
        self.rect.y = 170 - 35 * self.scale / 2

    def update(self, *args):
        pass


# класс текста в меню
class MenuText:
    def __init__(self, text):
        self.txt = text
        self.angle = 10
        self.is_increase = False
        self.font = pygame.font.Font("Pixel.ttf", 20)
        self.text = None

    # анимация
    def animate(self):
        if self.is_increase:
            self.angle += 0.1
        else:
            self.angle -= 0.1
        if self.angle <= 5:
            self.is_increase = True
        elif self.angle >= 15:
            self.is_increase = False
        self.text = self.font.render(self.txt, True, (100, 255, 100))
        self.text = pygame.transform.rotate(self.text, self.angle)


# класс кнопки
class Button(pygame.sprite.Sprite):
    def __init__(self, function, image):
        super().__init__(ui)
        self.function = function
        self.image = image
        self.image = pygame.transform.scale(self.image, (260, 90))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(470, 600)

    def update(self, *args):
        if args[0].type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(args[0].pos):
                self.function()


# класс планеты на фоне в меню
class Planet(pygame.sprite.Sprite):
    image = pygame.image.load("data/planets.png")

    def __init__(self):
        super().__init__(bg_objs)
        self.frames = []
        self.timer = 100
        self.cut_sheet(Planet.image, 2, 2)
        self.cur_frame = random.randint(0, 3)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(200, 500)
        self.drag = False
        self.touch_pos_x = 0
        self.touch_pos_y = 0
        self.target = 0
        self.a = 180
        self.r = 400
        self.center = (536, 600)
        self.target = (0, 0)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.x = self.rect.x
        self.y = self.rect.y
        if args[0].type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(args[0].pos):
                self.drag = True
                self.touch_pos_x = args[0].pos[0] - self.x
                self.touch_pos_y = args[0].pos[1] - self.y
        elif args[0].type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(args[0].pos):
                self.drag = False
                self.r = math.sqrt((self.x - self.center[0]) ** 2 + (self.y - self.center[1]) ** 2)
                self.target = (random.randint(0, 1200), random.randint(0, 400))
        elif pygame.mouse.get_focused() and args and args[0].type == pygame.MOUSEMOTION and self.drag:
            self.rect = self.rect.move(args[0].pos[0] - self.x - self.touch_pos_x,
                                       args[0].pos[1] - self.y - self.touch_pos_y)

    # передвижение планеты
    def move(self):
        if not self.drag:
            if self.timer == 0 or (self.rect.x // 100 == self.target[0] // 100
                                   and self.rect.y // 100 == self.target[1] // 100):
                self.timer = random.randint(0, 600)
                self.target = (random.randint(0, 1200), random.randint(0, 400))
            self.timer -= 1
            # поворот к рандомной точке
            x, y = self.target[0], self.target[0]
            rel_x, rel_y = x - self.rect.x, y - self.rect.y
            self.a = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
            v = -2
            vx = math.sin(self.a) * v
            vy = math.cos(self.a) * v
            self.rect = self.rect.move(vx, vy)
            # границы
            if self.rect.x < 0:
                self.rect.x += 1190
            elif self.rect.x > 1200:
                self.rect.x -= 1190
            if self.rect.y < 0:
                self.rect.y += 690
            elif self.rect.y > 700:
                self.rect.y -= 690


# класс блока
class Block(pygame.sprite.Sprite):
    image = pygame.image.load("data/block.png")

    def __init__(self, x, y, func):
        super().__init__(blocks)
        self.func = func
        self.image = Block.image
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


# класс бонуса
class Bonus(pygame.sprite.Sprite):
    def __init__(self, image, x, y, bonus):
        super().__init__(bonuses)
        self.bonus = bonus
        self.image = image
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if pygame.sprite.spritecollideany(self, all_sprites):
            bonus.play()
            self.bonus(ship)
            self.kill()


# класс дизлайка
class Dislike(pygame.sprite.Sprite):
    image = pygame.image.load("data/dislike.png")

    def __init__(self):
        super().__init__(decor)
        self.timer = 0
        self.image = Dislike.image
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()

    # передвижение
    def move(self):
        # анимация
        if self.timer == 0:
            self.image.set_alpha(0)
        else:
            self.timer -= 1
            if self.timer >= 80:
                self.image.set_alpha(self.image.get_alpha() + 10)
            if self.timer <= 20:
                self.image.set_alpha(self.image.get_alpha() - 10)
        self.rect.x = ship.rect.x - 48
        self.rect.y = ship.rect.y - 48

    def update(self, *args):
        if args[0].type == pygame.KEYDOWN:
            if args[0].key == 102:
                self.timer = 100
                self.image.set_alpha(55)


# загрузка сцены победы
def start_win():
    global win_text
    global ship, win
    pygame.mixer.music.pause()
    win.play()
    for i in blocks:
        i.kill()
    for i in bonuses:
        i.kill()
    for i in asteroids:
        i.kill()
    for i in red_ships:
        i.kill()
    win_text = Win()


# сцена победы
def win_scene():
    global win_text
    DrawParticles()
    win_text.animate()
    # частицы
    for x in range(random.randint(1, 4)):
        particle = Particle(0, 700, random.randint(0, 5), random.randint(-5, 0), random.randint(5, 10),
                            random.choice(colors))
        particles.append(particle)
    for x in range(random.randint(1, 4)):
        particle = Particle(1200, 700, random.randint(-5, 0), random.randint(-5, 0), random.randint(5, 10),
                            random.choice(colors))
        particles.append(particle)


# загруза сцены меню
def start_menu():
    global ship
    global menu_text, planet, logo
    for i in blocks:
        i.kill()
    for i in bonuses:
        i.kill()
    for i in asteroids:
        i.kill()
    for i in red_ships:
        i.kill()
    ship = Ship(x, y)
    planet = Planet()
    logo = Logo()
    ship.image = pygame.transform.scale(ship.original_image, (128, 128))
    ship.rect = ship.rect.move(-64, 86)
    ui.add(logo)
    play_button = Button(start_game, load_image("button.png"))
    menu_text = MenuText(menu_texts[random.randint(0, len(menu_texts) - 1)])


# сцена меню
def menu():
    pygame.mixer.music.unpause()
    global menu_text, logo, planet
    logo.animate()
    planet.move()
    menu_text.animate()
    screen.blit(menu_text.text, (800 - len(menu_text.txt) * 5, 300))
    pygame.display.flip()


# загрузка 1-го уровня
def lvl1():
    global lvl_id
    global dis
    dis = Dislike()
    lvl_id = 0
    for i in ui:
        i.kill()
    for i in bg_objs:
        if str(i) == "<Planet Sprite(in 1 groups)>":
            i.kill()
    for i in asteroids:
        i.kill()
    Border(5, 5, width - 5, 5)
    Border(5, height - 5, width - 5, height - 5)
    Border(5, 5, 5, height - 5)
    Border(width - 5, 5, width - 5, height - 5)
    blocks_coords = [(300, 300), (300, 364), (300, 236), (800, 300), (800, 364),
              (800, 236), (454, 100), (518, 100), (582, 100), (646, 100)]
    for i in blocks_coords:
        Block(i[0], i[1], None)
    xys = [(50, 50), (1150, 650)]
    for i in xys:
        EnemyShip(i[0], i[1])
    for i in range(5):
        Asteroid(load_image("asteroids.png"), 5, 1, random.randint(10, 30), random.randint(50, 1150),
                                   random.randint(50, 700), random.randint(0, 4))


# загрузка 2-го уровня
def lvl2():
    global lvl_id
    lvl_id = 1
    global ship
    global portal
    portal = None
    ship.image.set_alpha(255)
    ship.rect.x = 600
    ship.rect.y = 100
    for i in blocks:
        i.kill()
    for i in ui:
        i.kill()
    for i in bg_objs:
        if str(i) == "<Planet Sprite(in 1 groups)>":
            i.kill()
    for i in asteroids:
        i.kill()
    Border(5, 5, width - 5, 5)
    Border(5, height - 5, width - 5, height - 5)
    Border(5, 5, 5, height - 5)
    Border(width - 5, 5, width - 5, height - 5)
    Bonus(load_image("medicine_chest.png"), 120, 120, medicine_chest)
    blocks_coords = [(300, 108), (300, 172), (300, 236), (100, 300), (36, 236), (36, 172), (36, 108), (100, 44),
                     (164, 44), (228, 44), (836, 108), (836, 172), (836, 236), (1036, 300), (1100, 236), (1100, 172),
                     (1100, 108), (1036, 44), (972, 44), (908, 44)]
    for i in blocks_coords:
        Block(i[0], i[1], None)
    xys = [(200, 200), (1000, 200)]
    for i in xys:
        EnemyShip(i[0], i[1])
    for i in range(5):
        Asteroid(load_image("asteroids.png"), 5, 1, random.randint(10, 30), random.randint(50, 1150),
                                   random.randint(50, 700), random.randint(0, 4))


# загрузка 3-го уровня
def lvl3():
    global lvl_id
    lvl_id = 2
    global ship
    global portal
    portal = None
    ship.image.set_alpha(255)
    ship.rect.x = 600
    ship.rect.y = 350
    for i in blocks:
        i.kill()
    for i in ui:
        i.kill()
    for i in bg_objs:
        if str(i) == "<Planet Sprite(in 1 groups)>":
            i.kill()
    for i in asteroids:
        i.kill()
    Border(5, 5, width - 5, 5)
    Border(5, height - 5, width - 5, height - 5)
    Border(5, 5, 5, height - 5)
    Border(width - 5, 5, width - 5, height - 5)
    Bonus(load_image("medicine_chest.png"), 150, 150, medicine_chest)
    Bonus(load_image("x2.png"), 1050, 550, x2)
    blocks_coords = [(300, 200), (364, 200), (300, 264), (900, 500), (836, 500), (900, 436)]
    for i in blocks_coords:
        Block(i[0], i[1], None)
    xys = [(50, 50), (1086, 50), (1086, 586), (50, 586)]
    # создание турели
    for i in xys:
        es = EnemyShip(i[0], i[1])
        es.max_v = 0
        es.image = load_image("ships/gun.png")
        es.image = pygame.transform.scale(es.image, (64, 64))
        es.original_image = es.image

    for i in range(5):
        Asteroid(load_image("asteroids.png"), 5, 1, random.randint(10, 30), random.randint(50, 1150),
                                   random.randint(50, 700), random.randint(0, 4))


# загрузка 4-го уровня
def lvl4():
    global lvl_id
    lvl_id = 3
    global ship
    global portal
    portal = None
    ship.image.set_alpha(255)
    ship.rect.x = 1100
    ship.rect.y = 350
    for i in blocks:
        i.kill()
    for i in ui:
        i.kill()
    for i in bg_objs:
        if str(i) == "<Planet Sprite(in 1 groups)>":
            i.kill()
    for i in asteroids:
        i.kill()
    Border(5, 5, width - 5, 5)
    Border(5, height - 5, width - 5, height - 5)
    Border(5, 5, 5, height - 5)
    Border(width - 5, 5, width - 5, height - 5)
    Bonus(load_image("medicine_chest.png"), 464, 240, medicine_chest)
    Bonus(load_image("medicine_chest.png"), 464, 432, medicine_chest)
    blocks_coords = [(464, 496), (528, 496), (592, 496), (656, 496), (400, 432), (400, 240), (464, 176),
                     (528, 176), (592, 176), (656, 176), (720, 432), (720, 240), (720, 304), (720, 368)]
    for i in blocks_coords:
        Block(i[0], i[1], None)
    xys = [(656, 240), (656, 432)]
    for i in xys:
        es = EnemyShip(i[0], i[1])
        es.max_v = 0
        es.image = pygame.transform.scale(es.image, (64, 64))
        es.original_image = es.image
    xys = [(50, 50), (50, 650)]
    for i in xys:
        EnemyShip(i[0], i[1])
    for i in range(5):
        Asteroid(load_image("asteroids.png"), 5, 1, random.randint(10, 30), random.randint(50, 1150),
                                   random.randint(50, 700), random.randint(0, 4))


# уровни
def level():
    global dis
    global portal
    global ship
    global font
    global screen
    global lose
    if len(red_ships) == 0:
        if portal == None:
            portal = Portal(load_image("portal.png"), 8, 3, 472, 222)
            ship.portal = portal
        portal.animate()
    if ship not in all_sprites:
        lose.play()
        switch_scene(menu, start_menu)
    ship.drive()

    bonuses.update()
    text = font.render(str(ship.health) + "HP", True, (100, 255, 100))
    text1 = font.render("LVL" + str(lvl_id + 1), True, (100, 255, 100))
    text3 = font.render("CD: " + str(ship.cd), True, (100, 255, 100))
    if ship.protection_timer != 0:
        text4 = font.render("D: " + str(ship.protection_timer), True, (255, 100, 100))
        screen.blit(text4, (700, 50))
    if ship.x2timer != 0:
        text2 = font.render("X2: " + str(ship.x2timer), True, (255, 100, 100))
        screen.blit(text2, (900, 50))
    screen.blit(text, (10, 50))
    screen.blit(text1, (210, 50))
    screen.blit(text3, (410, 50))
    bg.paralax()
    dis.move()


if __name__ == '__main__':
    pygame.init()
    # загрузка звуков
    boom = pygame.mixer.Sound('sounds/boom.ogg')
    boom.set_volume(0.5)
    lose = pygame.mixer.Sound('sounds/lose.mp3')
    win = pygame.mixer.Sound('sounds/win.mp3')
    bonus = pygame.mixer.Sound("sounds/bonus.mp3")
    bonus.set_volume(0.7)
    shoot = pygame.mixer.Sound("sounds/shoot.mp3")
    shoot.set_volume(0.5)
    pygame.mixer.music.load('sounds/menu.mp3')
    pygame.mixer.music.play(-1)

    lvls = [lvl1, lvl2, lvl3, lvl4]
    lvl_id = 0
    pygame.display.set_caption("Space war")

    size = width, height = 1200, 700
    screen = pygame.display.set_mode(size)
    all_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    objects = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    red_ships = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    decor = pygame.sprite.Group()
    ui = pygame.sprite.Group()
    bg_objs = pygame.sprite.Group()
    bg = Background()
    ship = None
    dis = None
    pygame.font.init()
    running = True
    clock = pygame.time.Clock()
    portal = None
    menu_text = None
    text = None
    planet = None
    logo = None
    win_text = None
    font = pygame.font.Font("Pixel.ttf", 30)
    switch_scene(menu, start_menu)
    while running:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            all_sprites.update(event)
            bg_objs.update(event)
            ui.update(event)
            decor.update(event)
        red_ships.update()
        asteroids.update()
        objects.update()

        screen.fill((0, 0, 0))

        bg_objs.draw(screen)
        enemy_bullets.draw(screen)
        all_sprites.draw(screen)
        red_ships.draw(screen)
        objects.draw(screen)
        ui.draw(screen)
        asteroids.draw(screen)
        blocks.draw(screen)
        bonuses.draw(screen)
        decor.draw(screen)
        cur_scene()
        pygame.display.flip()
    pygame.quit()