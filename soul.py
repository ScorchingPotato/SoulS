import pygame
from utils import *
from ui import *
from world import *
import math,random

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
            self.i=0
            if self.hitd == 1: pygame.mixer.Sound("assets/sound/hit.mp3").play()
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

    def drawlight(self):
        pygame.draw.circle(self.game.lightmask, (0, 0, 0, 0), (self.rect.x+32,self.rect.y+32), self.lightradius*2)

    def draw(self):
        s = self.sprites[int(self.poe>0)][int(self.i*self.game.animspeed)%9]
        if self.hit and self.hitd<=10:
            s = s.copy()
            s.fill((255,255,255), special_flags=pygame.BLEND_RGB_ADD)
        self.game.screen.blit(s, self.rect.topleft)
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect,1);pygame.draw.rect(self.game.screen,(0,0,255),self.collrect,1)
        self.drawlight()
        self.i += 1


class Projectile(pygame.sprite.Sprite):
    def __init__(self,game,pos,speed,direction,targets=(),objects=()):
        super().__init__()
        self.game = game
        self.pos = pos
        self.speed = speed
        self.direction = direction
        self.rect = pygame.Rect(*pos, 32, 32)
        self.i = 0
        self.angle = 0
        self.lifetime = 0
        self.lifemax = 60
        self.game.projlayer.append(self)
        self.lightradius = 0
        self.targets = targets
        self.objects = objects

    def update(self):
        self.hit()

        self.lifetime += 1
        if self.lifetime >= self.lifemax:
            self.game.projlayer.remove(self)
            del self
        else:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

    def hit(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, self.objects) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax

            if isinstance(obj,self.targets) and obj.collrect.colliderect(self.rect.move(self.game.offset[0],self.game.offset[1])):
                self.lifetime = self.lifemax
                obj.poe -= 0.5
                obj.hit = True
                obj.rect.move_ip(self.direction*self.speed)
                obj.collrect.move_ip(self.direction*self.speed)

    def draw(self):
        image = pygame.transform.rotate(self.sprites[int(self.i * self.game.animspeed) % 4], self.angle)
        self.game.screen.blit(image, (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
        r = self.rect.move(self.game.offset[0],self.game.offset[1])
        pygame.draw.circle(self.game.lightmask, (0, 0, 0, 0), r.center, self.lightradius*2)
        self.i += 1

    def load_sprites(self,name=""):
        self.sprites = []
        for i in range(4):
            self.sprites.append(load_image(f"assets/{name}/{i}.png", 32))

class Flame(Projectile):
    def __init__(self,game,pos,speed,direction):
        super().__init__(game,pos,speed,direction,targets=Enemy,objects=(Lantern,Pillar))
        self.load_sprites("flame")
        self.lightradius = 16
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))+90

        pygame.mixer.Sound("assets/sound/flame.mp3").play()

    def hit(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax
                obj.lighten = True
                obj.lightradius = 192
                obj.l = 192
            if isinstance(obj,self.targets) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax
                obj.hp -= 0.5
                obj.hit = True

class Heart(Projectile):
    def __init__(self,game,pos,speed,direction):
        super().__init__(game,pos,speed,direction,targets=Player,objects=Lantern)
        self.load_sprites("heart")
        self.lightradius = 0

        pygame.mixer.Sound("assets/sound/sore.mp3").play()

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
            pygame.mixer.Sound("assets/sound/collect_poe.mp3").play()

    def draw(self):
        self.game.screen.blit(self.sprites[int(self.i*self.game.animspeed)%6], (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
        self.i += 1

class Soul(pygame.sprite.Sprite):
    def __init__(self,game,pos,name):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect(*pos, 64, 64)
        self.anchor = pos
        self.dest = pos
        self.direction = pygame.math.Vector2(0, 0)
        self.ylayer = pos[1]
        self.name = name
        self.load_sprites()
        self.i = 0 #Frame index
        self.speed = 1
        self.w = 0

    def load_sprites(self):
        self.sprites = []
        for i in range(9):
            self.sprites.append(load_image(f"assets/{self.name}/{i}.png", 64))

    def wander(self,w,m):
        self.w += 1
        if self.w >= w:
            self.w = 0
            self.dest = (self.anchor[0]+random.randint(-8,8)*8,self.anchor[1]+random.randint(-8,8)*8)
            self.direction = pygame.math.Vector2(self.dest[0]-self.rect.x,self.dest[1]-self.rect.y)
        if self.w==m:
            self.direction = pygame.math.Vector2(0,0)
        if self.direction.magnitude() > 0:
            self.direction.normalize_ip()
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

    def update(self):
        self.ylayer = self.rect.y + self.game.offset[1]
        self.wander(120,300)


    def draw(self):
        s=self.sprites[int(self.i*self.game.animspeed)%9]
        self.game.screen.blit(s, (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1);pygame.draw.circle(self.game.screen,(0,255,0),(self.anchor[0]+self.game.offset[0],self.anchor[1]+self.game.offset[1]),3)
        self.i += 1



class Enemy(pygame.sprite.Sprite):
    def __init__(self,game,pos,hp,speed,agro,attackrange,attackd):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect(*pos, 64, 64)
        self.collrect = pygame.Rect(pos[0]+8,pos[1]+34, 48, 32)
        self.direction = pygame.math.Vector2(0, 0)
        self.ylayer = pos[1]
        self.i = 0 #Frame index
        self.speed = speed
        self.hit = False
        self.hitd = 0
        self.agro = agro
        self.hp = hp

        self.attr = attackrange
        self.attw = 0
        self.attt = 0
        self.attd = attackd
        self.att = False

        self.targetd = pygame.math.Vector2(0, 0)
        self.ntg = pygame.math.Vector2(0, 0)
        self.path = [(0,0)]

    def load_sprites(self,name=""):
        self.sprites = []
        for i in range(9):
            self.sprites.append(load_image(f"assets/{name}/{i}.png", 64))
    def die(self):
        self.game.frontlayer.remove(self)
        self.game.frontlayer.append(Poe(self.game, (self.rect.x+16,self.rect.y+16)))

    def pathfind(self,obstacles=(Lantern,Pillar)):
        r = self.rect.move(self.game.offset[0],self.game.offset[1])
        self.targetd = pygame.math.Vector2(self.game.player.rect.x-r.x,self.game.player.rect.y-r.y)
        if self.targetd.magnitude() > 0:
            self.ntg = self.targetd.normalize()
        if not self.att:
            self.direction = pygame.math.Vector2(0, 0)

        if self.targetd.magnitude() <= self.agro:
            objects = []
            for w in self.game.backlayer:
                for r in w.trects:
                    objects.append(r.move(self.game.offset[0]+w.pos[0],self.game.offset[1]+w.pos[1]))
            for obj in self.game.frontlayer:
                if isinstance(obj, obstacles):
                    objects.append(obj.rect.move(self.game.offset[0],self.game.offset[1]))
            self.path = pathfind((math.floor(self.rect.x+32+self.game.offset[0]),math.floor(self.rect.y+32+self.game.offset[1])),(math.floor(self.game.player.rect.x+32),math.floor(self.game.player.rect.y+32)),objects)
            if not self.path: self.path = [(0,0)]

            if not self.att:
                self.direction = pygame.Vector2(self.path[0][0], self.path[0][1])

    def move(self):
        if self.direction.magnitude() > 0:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.collrect.topleft = (self.rect.x+8,self.rect.y+34)

    def update(self):
        if self.hp <= 0:
            self.die()
        if self.hit:
            self.hitd += 1
            self.i=0
            if self.hitd == 1: pygame.mixer.Sound("assets/sound/hit.mp3").play()
            if self.hitd >= 30:
                self.hit = False
                self.hitd = 0
        self.ylayer = self.rect.y + self.game.offset[1]
        self.pathfind()
        self.attack()
        self.move()


    def attack(self):
        pass

    def draw(self):
        s=self.sprites[int(self.i*self.game.animspeed)%9]
        if self.hit and self.hitd<=10:
            s = s.copy()
            s.fill((255,255,255), special_flags=pygame.BLEND_RGB_ADD)
        self.game.screen.blit(s, (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: 
            pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
            pygame.draw.rect(self.game.screen,(0,0,255),self.collrect.move(self.game.offset[0],self.game.offset[1]),1)
            pygame.draw.circle(self.game.screen,(0,255,0),self.rect.move(self.game.offset[0],self.game.offset[1]).center, self.agro, 1)
    
        self.i += 1


class Anger(Enemy):
    def __init__(self,game,pos):
        super().__init__(game,pos,1,1,300,150,60)
        self.load_sprites("anger")
        self.speed = 1
        self.hit = False
        self.hitd = 0

    def attack(self):
        if self.targetd.magnitude() <= self.attr and not self.att and abs(self.path[0][0]-self.ntg.x)<=0.3 and abs(self.path[0][1]-self.ntg.y)<=0.3:
            self.attw += 1

        if self.attw >= 30:
            self.att = True
            self.attt += 1
        if self.attt == self.attd:
            self.attw = 0
            self.attt = 0
            self.att = False

        if self.attt == 1:
            self.d = self.ntg
            pygame.mixer.Sound("assets/sound/fire_dash.mp3").play()

        if self.attt > 0:
            self.direction = self.d*5*(15/self.attt)

        if self.att and self.collrect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.collrect) and not self.game.player.hit:
            self.game.player.poe -= 0.5
            self.game.player.hit = True
            self.game.offset[0] -= self.direction.x
            self.game.offset[1] -= self.direction.y

class Lust(Enemy):
    def __init__(self,game,pos):
        super().__init__(game,pos,1,1,300,250,60)
        self.load_sprites("lust")
        self.speed = 1
        self.hit = False
        self.hitd = 0

    def attack(self):
        if self.targetd.magnitude() <= self.attr and not self.att:
            self.attw += 1
            self.direction = pygame.Vector2(self.path[0][0], self.path[0][1])

        if self.attw >= 60:
            self.att = True
            self.attt += 1
        if self.attt == self.attd:
            self.attw = 0
            self.attt = 0
            self.att = False
        if self.attt == 1:
            Heart(self.game,(self.rect.x+32,self.rect.y+32), 5, self.ntg)