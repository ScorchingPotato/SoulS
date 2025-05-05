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

    def draw(self):
        self.update()
        s = self.sprites[int(self.poe>0)][int(self.i*self.game.animspeed)%9]
        if self.hit and self.hitd<=10:
            s = s.copy()
            s.fill((255,255,255), special_flags=pygame.BLEND_RGB_ADD)
        self.game.screen.blit(s, self.rect.topleft)
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

        pygame.mixer.Sound("assets/sound/flame.mp3").play()

    def update(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax

            if type(obj) in [Anger,Lust] and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax
                obj.hp -= 0.5
                obj.hit = True
                obj.rect.x += self.direction.x * self.speed
                obj.rect.y += self.direction.y * self.speed


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

class Heart:
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

        pygame.mixer.Sound("assets/sound/sore.mp3").play()

    def update(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.collrect.colliderect(self.rect):
                self.lifetime = self.lifemax

            if type(obj) is Player and obj.collrect.colliderect(self.rect.move(self.game.offset[0],self.game.offset[1])):
                self.lifetime = self.lifemax
                obj.poe -= 0.5
                obj.hit = True


        self.lifetime += 1
        if self.lifetime >= self.lifemax:
            self.game.projlayer.remove(self)
            del self
        else:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed

    def load_sprites(self):
        self.sprites = []
        for i in range(4):
            self.sprites.append(load_image(f"assets/heart/{i}.png", 32))
        

    def draw(self):
        self.update()
        image = self.sprites[int(self.i * self.game.animspeed) % 4]
        self.game.screen.blit(image, (self.rect.x+self.game.offset[0],self.rect.y+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(255,0,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
        self.i += 1

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
        self.hit = False
        self.hitd = 0
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
        if self.hit:
            self.hitd += 1
            self.i=0
            if self.hitd == 1: pygame.mixer.Sound("assets/sound/hit.mp3").play()
            if self.hitd >= 30:
                self.hit = False
                self.hitd = 0
        self.ylayer = self.rect.y + self.game.offset[1]
        r = self.rect.move(self.game.offset[0],self.game.offset[1])
        targetd = pygame.math.Vector2(self.game.player.rect.x-r.x,self.game.player.rect.y-r.y)
        if targetd.magnitude() > 0:
            ntg = targetd.normalize()
        if not self.leep:
            self.direction = pygame.math.Vector2(0, 0)

        if targetd.magnitude() <= self.agro:
            objects = []
            for w in self.game.backlayer:
                for r in w.trects:
                    objects.append(r.move(self.game.offset[0]+w.pos[0],self.game.offset[1]+w.pos[1]))
            for obj in self.game.frontlayer:
                if isinstance(obj, Lantern):
                    objects.append(obj.rect.move(self.game.offset[0],self.game.offset[1]))
            self.path = pathfind((math.floor(self.rect.x+32+self.game.offset[0]),math.floor(self.rect.y+32+self.game.offset[1])),(math.floor(self.game.player.rect.x+32),math.floor(self.game.player.rect.y+32)),objects)
            if not self.path: self.path = [(0,0)]

        
        if targetd.magnitude() <= 150 and not self.leep and abs(self.path[0][0]-ntg.x)<=0.3 and abs(self.path[0][1]-ntg.y)<=0.3:
            self.leepw += 1
        
        elif targetd.magnitude() <= self.agro and not self.leep:
            self.direction = pygame.Vector2(self.path[0][0], self.path[0][1])

        if self.leepw >= 30:
            self.leep = True
            self.leept += 1
        if self.leept == self.leeptime:
            self.leepw = 0
            self.leept = 0
            self.leep = False

        if self.leept == 1:
            self.d = ntg
            pygame.mixer.Sound("assets/sound/fire_dash.mp3").play()

        if self.leept > 0:
            self.direction = self.d*self.lspd*(15/self.leept)

        # Normalize and apply movement
        if self.direction.magnitude() > 0:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.collrect.topleft = (self.rect.x+8,self.rect.y+34)  # Update collrect position

        if self.leep and self.collrect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.collrect) and not self.game.player.hit:
            self.game.player.poe -= 0.5
            self.game.player.hit = True
            self.game.offset[0] -= self.direction.x
            self.game.offset[1] -= self.direction.y


    def draw(self):
        self.update()
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

class Lust(pygame.sprite.Sprite):
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
        self.hit = False
        self.hitd = 0
        self.agro = 300

        self.hp = 1

        self.shw = 0
        self.sht = 0
        self.shtime = 20
        self.shoot = False

    def load_sprites(self):
        self.sprites = []
        for i in range(9):
            self.sprites.append(load_image(f"assets/lust/{i}.png", 64))

    def die(self):
        self.game.frontlayer.remove(self)
        self.game.frontlayer.append(Poe(self.game, (self.rect.x+16,self.rect.y+16)))

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
        r = self.rect.move(self.game.offset[0],self.game.offset[1])
        targetd = pygame.math.Vector2(self.game.player.rect.x-r.x,self.game.player.rect.y-r.y)
        if targetd.magnitude() > 0:
            ntg = targetd.normalize()
        self.direction = pygame.math.Vector2(0,0)

        if targetd.magnitude() <= self.agro:
            objects = []
            for w in self.game.backlayer:
                for r in w.trects:
                    objects.append(r.move(self.game.offset[0]+w.pos[0],self.game.offset[1]+w.pos[1]))
            for obj in self.game.frontlayer:
                if isinstance(obj, Lantern):
                    objects.append(obj.rect.move(self.game.offset[0],self.game.offset[1]))
            self.path = pathfind((math.floor(self.rect.x+32+self.game.offset[0]),math.floor(self.rect.y+32+self.game.offset[1])),(math.floor(self.game.player.rect.x+32),math.floor(self.game.player.rect.y+32)),objects)
            if not self.path: self.path = [(0,0)]

        
        if targetd.magnitude() <= self.agro and not self.shoot:
            self.shw += 1
            self.direction = pygame.Vector2(self.path[0][0], self.path[0][1])

        if self.shw >= 60:
            self.shoot = True
            self.sht += 1
        if self.sht == self.shtime:
            self.shw = 0
            self.sht = 0
            self.shoot = False
        if self.sht == 1:
            Heart(self.game,(self.rect.x+32,self.rect.y+32), 5, ntg)

        # Normalize and apply movement
        if self.direction.magnitude() > 0:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.collrect.topleft = (self.rect.x+8,self.rect.y+34)  # Update collrect position


    def draw(self):
        self.update()
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