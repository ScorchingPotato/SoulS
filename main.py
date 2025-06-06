import pygame
from soul import *
from world import *
from ui import *
from constructor import *
import maptiles as Map

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Soul Search")
        self.clock = pygame.time.Clock()
        self.screen = pygame.Surface((1200, 800))
        self.lightmask = pygame.Surface((1200, 800), pygame.SRCALPHA)
        self.lightmask.fill((0, 0, 0))


        #DEBUG
        self.debugrect = True
        self.debugdark = True

        self.offset = [0,0]
        self.animspeed = 0.2

        self.stop = False

        #Dialogue dim = (768,122)

        self.uilayer = [DialogueBox(self,[Dialogue(f"Test {i}",(768,122)) for i in range(3)])]
        self.projlayer = []
        self.player = Player(self, (568, 368))

        self.decorlayer = [Decor(self,"grass",(256,196))]
        self.frontlayer = [self.player,Soul(self,(-500,100),"wanderer"),Poe(self,(100,100)),Poe(self,(100,800)),Lantern(self,(600,200)),Lust(self,(-1000,500)),Anger(self,(1400, 400)),Pillar(self,(600, 0),3,"n"),Pillar(self,(800,0),5,'b')]
        self.backlayer = [construct(Map.e,self,(0,0)),construct(Map.test1x1,self,(600,600))]

        self.rungame = True

        pygame.mixer.music.load("assets/sound/main_soundtrack.mp3")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)

    def run(self):
        while self.rungame:
            self.clock.tick(60)
            print(f"FPS: {self.clock.get_fps():.2f}", end="\r")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rungame = False
                if event.type == pygame.KEYDOWN:
                    if (event.mod & pygame.KMOD_CTRL):
                        if event.key == pygame.K_h:
                            print("DEBUGGING:\nctrl+b = toggle dark\nctrl+r = toggle rect\nctrl+'+' =  +1 poe")
                        if event.key == pygame.K_b:
                            self.debugdark = not self.debugdark
                        if event.key == pygame.K_r:
                            self.debugrect = not self.debugrect
                        if event.key == pygame.K_KP_PLUS:
                            self.player.poe += 1

            if not self.stop:
                self.update()
            self.draw()
            self.display()

            pygame.display.flip()
            self.screen.fill((20, 10, 40))


    def draw(self):

        for s in self.backlayer:s.draw()

        for s in self.decorlayer:s.draw()

        for s in sorted(self.frontlayer, key=lambda x:x.ylayer):s.draw()

        for s in self.projlayer:s.draw()

        for s in self.uilayer:s.draw()

    def update(self):
        for s in self.frontlayer:s.update()

        for s in self.projlayer:s.update()

    def display(self):
        a = (255,0,0,15) if self.debugdark else (0,0,0)
        self.window.blit(self.screen, (0, 0))
        self.window.blit(self.lightmask, (0, 0))
        self.lightmask.fill(a)
        for s in self.uilayer:s.draw()

if __name__ == "__main__":
    game = Game()
    game.run()