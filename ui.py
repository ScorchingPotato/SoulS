import pygame,math
from utils import *

class Interact(pygame.sprite.Sprite):
    def __init__(self,game,pos,icon,text):
        super().__init__()
        self.game = game
        self.rect = pygame.Rect(*pos, 64, 64)
        self.icon = load_image(f"assets/ui/{icon}.png", 16)
        self.text = text
        self.font = pygame.font.Font("assets/font.ttf", 24)
        self.textsurface = self.font.render(self.text, True, (255, 255, 255))
        self.drawbox()

        self.visible = True

    def drawbox(self):
        self.box = pygame.Surface((self.textsurface.get_width()+112, 32), pygame.SRCALPHA)
        self.box.blit(load_image("assets/ui/interbox_corner.png",32), (0, 0))
        self.box.blit(pygame.transform.flip(load_image("assets/ui/interbox_corner.png",32),True,False), (self.textsurface.get_width()+32, 0))
        self.box.blit(load_image("assets/ui/interbox_body.png",(self.textsurface.get_width(),32)), (32, 0))

        self.box.blit(self.icon, (16, 8))
        self.box.blit(self.textsurface, (48, 0))

        
    def draw(self):
        if self.visible: self.game.screen.blit(self.box, (self.rect.x+self.game.offset[0], self.rect.y+self.game.offset[1]))


class ManaPoe:
    def __init__(self,wrapper,pos,strenght=0):
        self.s = strenght
        self.w = wrapper
        self.pos = pos
        self.img = load_image(f"assets/ui/mana/{self.s}.png", 32)

class ManaBar:
    def __init__(self,game,pos,player):
        self.game = game
        self.pos = pos
        self.player = player
        self.manapoes = [ManaPoe(self,(i*32,0),m) for i,m in enumerate(self.calc_mana())]
        self.box = pygame.Surface((self.player.maxpoe*32+16, 32), pygame.SRCALPHA)

    def drawbox(self):
        for mana in self.manapoes:
            self.box.blit(mana.img, (mana.pos[0]+8, self.pos[1]))

    def calc_mana(self):
        m = [1 for _ in range(math.floor(self.player.poe))]
        if self.player.poe % 1 == 0.5: m.append(0.5)
        em = [0 for _ in range(math.floor(self.player.maxpoe)-math.floor(self.player.poe))]
        return m+em
    
    def update(self):
        self.manapoes = [ManaPoe(self,(i*32,0),m) for i,m in enumerate(self.calc_mana())]
        self.drawbox()

    def draw(self):
        self.update()
        self.game.window.blit(self.box, (self.pos[0], self.pos[1]))
