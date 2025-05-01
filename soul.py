import pygame
from utils import *
from ui import *
from world import *
import math

class Player(pygame.sprite.Sprite):
    def __init__(self,game,pos):
        super().__init__()
        self.game = game
        self.cx,self.cy = pos
        self.rect = pygame.Rect(*pos, 64, 64)
        self.collrect = pygame.Rect(pos[0]+8,pos[1]+34, 48, 30)
        self.ylayer = pos[1]
        self.poe = 0
        self.maxpoe = 3
        self.hit = False
        self.hitd = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.canceldir = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.i = 0 #Frame index
        self.load_sprites()

        self.shoott = 0

        self.lightradius = 96

        self.manabar = ManaBar(self.game, (0,0), self)
        self.game.uilayer.append(self.manabar)

    def update(self):
        if self.poe < 0: pass#self.game.rungame = False
        if self.poe >= self.maxpoe: self.poe = self.maxpoe
        if self.poe > 0: self.lightradius += 1
        else: self.lightradius -= 1
        self.lightradius = max(min(128,self.lightradius),96)

        self.ylayer = self.rect.y
        keys = pygame.key.get_pressed()
        self.direction = pygame.math.Vector2(0, 0)

        if self.hit:
            self.hitd += 1
            if self.hitd >= 30:
                self.hit = False
                self.hitd = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
        if keys[pygame.K_d]:
            self.direction.x = 1
        if keys[pygame.K_w]:
            self.direction.y = -1
        if keys[pygame.K_s]:
            self.direction.y = 1
        if keys[pygame.K_SPACE]:
            self.shoott += 1
        elif self.poe >= 0.5 and self.shoott >= 30:
            mx,my = pygame.mouse.get_pos()
            Flame(self.game, (self.rect.x+32-self.game.offset[0],self.rect.y+32-self.game.offset[1]), 6, pygame.Vector2(mx-568-32,my-368-32).normalize())
            self.poe -= 0.5
            self.shoott = 0
                

        if self.direction.magnitude() > 0:
            self.direction.normalize_ip()
        self.game.offset[0] -= (self.direction.x-self.canceldir.x) * self.speed 
        self.game.offset[1] -= (self.direction.y-self.canceldir.y) * self.speed

        self.canceldir = pygame.math.Vector2(0, 0)

    def load_sprites(self):
        self.sprites = []
        a = []
        for p in range(2):
            for i in range(9):
                a.append(load_image(f"assets/{p}spirit/{i}.png", 64))
            self.sprites.append(a)
            a = []

    def draw(self):
        self.update()
        self.game.screen.blit(self.sprites[int(self.poe>0)][int(self.i*self.game.animspeed)%9], self.rect.topleft)
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect,1);pygame.draw.rect(self.game.screen,(0,0,255),self.collrect,1)
        pygame.draw.circle(self.game.lightmask, (0, 0, 0, 0), (self.rect.x+32,self.rect.y+32), self.lightradius*2)
        self.i += 1

class Flame:
    def __init__(self,game,pos,speed,direction):
        self.game = game
        self.pos = pos
        self.speed = speed
        self.direction = direction
        self.load_sprites()
        self.rect = pygame.Rect(*pos, 32, 32)
        self.i = 0
        self.lifetime = 0
        self.lifemax = 60
        self.game.projlayer.append(self)
        self.lightradius = 16

        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))+90

    def update(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax

            if isinstance(obj, Anger) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax
                obj.hp -= 0.5


        self.lifetime += 1
        if self.lifetime >= self.lifemax:
            self.game.projlayer.remove(self)
            del self
        else:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

        

    def draw(self):
        self.update()
        image = pygame.transform.rotate(self.sprites[int(self.i * self.game.animspeed) % 4], self.angle)
        self.game.screen.blit(image, (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
        r = self.rect.move(self.game.offset[0],self.game.offset[1])
        pygame.draw.circle(self.game.lightmask, (0, 0, 0, 0), (r.x+16,r.y+16), self.lightradius*2)
        self.i += 1

    def load_sprites(self):
        self.sprites = []
        for i in range(4):
            self.sprites.append(load_image(f"assets/flame/{i}.png", 32))

class Poe(pygame.sprite.Sprite):
    def __init__(self,game,pos):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect(*pos, 32, 32)
        self.ylayer = pos[1]
        self.load_sprites()
        self.i = 0 #Frame index

    def load_sprites(self):
        self.sprites = []
        for i in range(6):
            self.sprites.append(load_image(f"assets/poe/{i}.png", 32))

    def update(self):
        self.ylayer = self.rect.y+self.game.offset[1]-self.rect.height
        if self.rect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.rect):
            self.game.player.poe += 1
            self.game.frontlayer.remove(self)

    def draw(self):
        self.update()
        self.game.screen.blit(self.sprites[int(self.i*self.game.animspeed)%6], (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
        self.i += 1


class Anger(pygame.sprite.Sprite):
    def __init__(self,game,pos):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect(*pos, 64, 64)
        self.collrect = pygame.Rect(pos[0]+8,pos[1]+34, 48, 32)
        self.direction = pygame.math.Vector2(0, 0)
        self.ylayer = pos[1]
        self.load_sprites()
        self.i = 0 #Frame index
        self.speed = 1
        self.avoid = False
        self.agro = 300

        self.hp = 1

        self.leepw = 0
        self.leept = 0
        self.leeptime = 60
        self.lspd = 5
        self.leep = False
        self.d = pygame.math.Vector2(0, 0)

    def load_sprites(self):
        self.sprites = []
        for i in range(9):
            self.sprites.append(load_image(f"assets/anger/{i}.png", 64))

    def die(self):
        self.game.frontlayer.remove(self)
        self.game.frontlayer.append(Poe(self.game, (self.rect.x+16,self.rect.y+16)))

    def update(self):
        if self.hp <= 0:
            self.die()
        self.avoid = False
        self.ylayer = self.rect.y + self.game.offset[1]

        # Calculate direction toward the player
        r = self.rect.move(self.game.offset[0], self.game.offset[1])
        target_direction = pygame.Vector2(
            self.game.player.rect.centerx - r.centerx,
            self.game.player.rect.centery - r.centery
        )

        # Avoid obstacles (Lanterns)
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.collrect.colliderect(self.collrect):
                # Calculate avoidance vector
                avoidance = pygame.Vector2(
                    self.collrect.centerx - obj.collrect.centerx,
                    self.collrect.centery - obj.collrect.centery
                )
                if avoidance.magnitude() > 0:
                    avoidance = avoidance.normalize() * 100  # Scale avoidance force
                    target_direction += avoidance
                    self.avoid = True


        if self.leep:
            self.rect.x += self.d.x*self.lspd
            self.rect.y += self.d.y*self.lspd
            self.collrect.topleft = (self.rect.x+8,self.rect.y+34)
            if self.collrect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.collrect) and not self.game.player.hit:
                self.game.player.poe -= 0.5
                self.game.player.hit = True

        if target_direction.magnitude() < 100 and not self.avoid:
            self.leepw += 1
        else:
            self.speed = 1
            if not self.leep:
                self.leepw = 0

        
        if self.leept == 1:
            self.d = target_direction.normalize()

        if self.leepw >= 30:
            self.leep = True
            self.leept += 1
        if self.leept == self.leeptime:
            self.leepw=0
            self.leept=0
            self.leep = False

        # Normalize and apply movement
        if target_direction.magnitude() > 0 and self.leepw == 0 and target_direction.magnitude() < self.agro:
            self.direction = target_direction.normalize()
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.collrect.topleft = (self.rect.x+8,self.rect.y+34)  # Update collrect position


    def draw(self):
        self.update()
        self.game.screen.blit(self.sprites[int(self.i*self.game.animspeed)%9], (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: 
            pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
            pygame.draw.rect(self.game.screen,(0,0,255),self.collrect.move(self.game.offset[0],self.game.offset[1]),1)
            pygame.draw.circle(self.game.screen,(0,255,0),self.rect.move(self.game.offset[0],self.game.offset[1]).center, self.agro, 1)
    
        self.i += 1