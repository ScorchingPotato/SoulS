import pygame
from utils import *
from ui import *

class Decor:
    def __init__(self,game,type,pos):
        self.img = load_image(f"assets/decor/{type}.png", 16)
        self.pos = pos
        self.game = game
        self.collrect = None
    def draw(self):
        self.game.screen.blit(self.img, (self.pos[0]+self.game.offset[0], self.pos[1]+self.game.offset[1]))

class Tile(pygame.sprite.Sprite):
    def __init__(self,name,pos,type="",rotation=0,collrect=pygame.Rect(0,0,0,0)):
        super().__init__()
        self.name = name
        self.type = type
        self.prefix = "-" if type else ""
        self.rect = pygame.Rect(*pos, 64, 64)
        self.collrect = collrect

        self.img = pygame.transform.rotate(load_image(f"assets/tiles/{name}{self.prefix}{type}.png", 64), rotation)
    
class Wrapper:
    def __init__(self,game,pos,tiles,res):
        self.game = game
        self.pos = pos
        self.tiles = tiles
        self.surf = pygame.Surface(res, pygame.SRCALPHA)
        self.rect = pygame.Rect(*pos,*res)
        self.debugsurf = pygame.Surface(res, pygame.SRCALPHA)
        self.trects = []
        self.drawsurface()

    def drawsurface(self):
        for t in self.tiles:
            self.surf.blit(t.img, (t.rect.x, t.rect.y))
            self.trects.append(t.collrect)
            #pygame.draw.rect(self.debugsurf,(255,255,0),t.rect,1)
        self.trects = compress_rects(self.trects)
        for r in self.trects:
            pygame.draw.rect(self.debugsurf,(255,255,255),r,1)

    def update(self):
        for r in self.trects:
            if r.move(self.game.offset[0]+self.pos[0],self.game.offset[1]+self.pos[1]).colliderect(self.game.player.collrect):
                self.game.player.canceldir = self.game.player.direction

    def draw(self):
        self.update()
        self.game.screen.blit(self.surf, (self.pos[0]+self.game.offset[0], self.pos[1]+self.game.offset[1]))
        if self.game.debugrect: 
            pygame.draw.rect(self.game.screen,(255,255,0),self.rect.move(self.game.offset[0],self.game.offset[1]),1)
            self.game.screen.blit(self.debugsurf, (self.pos[0]+self.game.offset[0], self.pos[1]+self.game.offset[1]))

class Pillar:
    def __init__(self, game, pos, size, state, n=(0, 0)):
        self.img = load_image(f"assets/decor/pillar.png", 64)
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1] - self.size * 64, 64, self.size * 64)
        self.collrect = pygame.Rect(pos[0] + 8, pos[1] - 32, 48, 32)
        self.pos = pos
        self.game = game
        self.ylayer = pos[1]
        self.state = state
        self.n = n
        self.sprite()

    def sprite(self):
        self.img = pygame.Surface((64, self.size * 64), pygame.SRCALPHA)
        for i in range(self.size):
            if i == 0:
                self.img.blit(load_image(f"assets/decor/pillar/{self.state if not self.state == 'b' else 's'}bot.png", 64), (0, self.size * 64 - 64))
            elif i == self.size - 1:
                self.img.blit(load_image(f"assets/decor/pillar/{self.state}top.png", 64), (0, 0))
            else:
                self.img.blit(load_image(f"assets/decor/pillar/{self.state if not self.state == 'b' else 's'}mid.png", 64), (0, i * 64))

    def cast_shadow(self, light_source, multiplier=1500):
        """Cast a shadow based on the light source."""
        light_pos = pygame.math.Vector2(light_source)
        pillar_pos = pygame.math.Vector2(self.collrect.center)
        pillar_pos += pygame.math.Vector2(*self.game.offset)

        # Calculate the direction vector and distance
        direction = pillar_pos - light_pos
        distance = direction.length()

        if distance == 0:  # Avoid division by zero
            return

        # Normalize the direction vector
        direction = direction.normalize()

        # Calculate shadow length
        shadow_length = (1 / math.sqrt(distance)) * multiplier

        # Create a shadow mask from the pillar's sprite
        s = self.img.copy()
        s.fill((0, 0, 0, min(1020/math.sqrt(distance),255)), special_flags=pygame.BLEND_RGBA_MULT)  # Darken the shadow mask
        s = pygame.transform.scale(s, (64+(distance/multiplier),shadow_length))
        angle = math.degrees(math.atan2(direction.y, -direction.x)) + 90
        s = pygame.transform.rotate(s, angle)  # Rotate the shadow mask

        # Calculate the position to blit the shadow
        shadow_rect = s.get_rect(center=pillar_pos + direction * (shadow_length / 2))

        # Blit the shadow mask onto the screen
        self.game.screen.blit(s, shadow_rect.topleft)

    def update(self):
        for obj in self.game.frontlayer:
            if isinstance(obj, Lantern) and obj.lighten:
                self.cast_shadow(obj.collrect.move(self.game.offset[0],self.game.offset[1]).center, multiplier=2000)
        if self.game.player.poe > 0:
            self.cast_shadow(self.game.player.rect.center)
        self.ylayer = self.rect.y + self.game.offset[1] - 8 + (self.size - 1) * 64
        if self.collrect.move(self.game.offset[0], self.game.offset[1]).colliderect(self.game.player.collrect):
            self.game.player.canceldir = self.game.player.direction

    def draw(self):
        self.game.screen.blit(self.img, (self.rect.x + self.game.offset[0], self.rect.y + self.game.offset[1]))
        if self.game.debugrect:
            pygame.draw.rect(self.game.screen, (0, 0, 255), self.collrect.move(self.game.offset[0], self.game.offset[1]), 1)
            pygame.draw.rect(self.game.screen, (255, 0, 0), self.rect.move(self.game.offset[0], self.game.offset[1]), 1)

class Lantern:
    def __init__(self,game,pos):
        self.img = load_image(f"assets/decor/lantern.png", 64)
        self.rect = pygame.Rect(*pos, 64, 64)
        self.collrect = pygame.Rect(pos[0]+16,pos[1]+48, 32, 16)
        self.pos = pos
        self.game = game
        self.lighten = False
        self.lightsprites = []
        self.load_sprites()
        self.i = 0
        self.ylayer = pos[1]

        self.lightradius = 192
        self.l = self.lightradius//2
        self.ib = Interact(self.game, (self.rect.x-32,self.rect.y-32), "key_e", "Light up")
        self.game.uilayer.append(self.ib)

    def load_sprites(self):
        for i in range(4):
            self.lightsprites.append(load_image(f"assets/light/{i}.png", 64))

    def update(self):
        keys = pygame.key.get_pressed()
        self.ylayer = self.rect.y+self.game.offset[1]-8
        if self.lighten: self.l+=1;self.l=min(self.l, self.lightradius)
        if self.rect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.rect) and self.game.player.poe >= 1 and not self.lighten:
            self.ib.visible = True
            if keys[pygame.K_e]:
                pygame.mixer.Sound("assets/sound/light_lantern.mp3").play()
                self.lighten = True
                self.game.player.poe -= 1
                self.game.uilayer.remove(self.ib)
        else:
            self.ib.visible = False

        if self.collrect.move(self.game.offset[0],self.game.offset[1]).colliderect(self.game.player.collrect):
            self.game.player.canceldir = self.game.player.direction

    def draw(self):
        self.update()
        self.game.screen.blit(self.img, (self.pos[0]+self.game.offset[0], self.pos[1]+self.game.offset[1]))
        if self.lighten:
            r = self.rect.move(self.game.offset[0],self.game.offset[1])
            pygame.draw.circle(self.game.lightmask, (0, 0, 0, 0), (r.x+32,r.y+32), self.l*2)
            self.game.screen.blit(self.lightsprites[int(self.i*self.game.animspeed)%4], (self.pos[0]+self.game.offset[0], self.pos[1]+self.game.offset[1]))
        if self.game.debugrect: pygame.draw.rect(self.game.screen,(0,0,255),self.collrect.move(self.game.offset[0],self.game.offset[1]),1)
        self.i += 1