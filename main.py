# Created by Dogan AY - Enzo SANA

import random
import shelve

from props.enemy import Enemy
from props.ship import Ship
from utils.constants import *
from utils.gameUtils import collide
from utils.particule_spawner import ParticuleSpawner

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.music.load(MP3)
pygame.mixer.music.set_volume(.2)
pygame.mixer.music.play(-1)


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs, particule_spawner):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        particule_spawner.spawn_particule(obj.x, obj.y)
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            return True

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


def main():
    run = True
    FPS = 60
    level = 0
    score = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 7

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    particule_spawner = ParticuleSpawner()

    def redraw_window():
        WIN.blit(BG, (0, 0))

        lives_label = main_font.render("Lives: " + str(lives), 1, (255, 255, 255))
        score_label = main_font.render("Score: " + str(score), 1, (255, 255, 255))
        level_label = main_font.render("Level: " + str(level), 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - level_label.get_width() - 30, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        particule_spawner.particule_group.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255, 255, 255))
            WIN.blit(lost_label, ((WIDTH - lost_label.get_width()) / 2, (HEIGHT - lost_label.get_height()) / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        particule_spawner.update()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                sf = shelve.open(HIGHEST_SCORE)
                try:
                    if sf['score'] < score:
                        sf['score'] = score
                except KeyError:
                    pass
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player, particule_spawner)

            if random.randrange(0, int((1 / level) * 200)) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        if player.move_lasers(-laser_vel, enemies, particule_spawner):
            score += 100


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    count = 0
    colors = [(255, 255, 255), (0, 0, 0)]
    sf = shelve.open(HIGHEST_SCORE)

    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, colors[0])
        WIN.blit(title_label, ((WIDTH - title_label.get_width()) / 2, (HEIGHT - title_label.get_height()) / 2))
        try:
            score = sf['score']
            count += 1
            if score != 0:
                highest_score_label = title_font.render("HIGHEST SCORE : " + str(score), 1, colors[(count % 2)])
                WIN.blit(highest_score_label, ((WIDTH - highest_score_label.get_width()) / 2,
                                               HEIGHT / 2 - title_label.get_height() - highest_score_label.get_height() / 2))
        except KeyError:
            pass
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
        clock = pygame.time.Clock()
        clock.tick(10)
    pygame.quit()
    sf.close()


main_menu()
