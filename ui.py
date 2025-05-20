import pygame,math
from utils import *

pygame.init()
pygame.font.init()

class TextBlock:
    def __init__(self,text,x,y,flag=[],fontsize=24):
        self.text = text
        self.x = x
        self.y = y
        self.flag = flag
        self.len = len(text)
        self.i = -1
        self.font = pygame.font.Font("assets/font.ttf", fontsize)
        if 'b' in flag:self.font.set_bold(True)
        if 'i' in flag:self.font.set_italic(True)
        if 'u' in flag:self.font.set_underline(True)
        if 'h' in flag:self.c=(110,90,130) 
        else: self.c=(20,10,40)
        self.render()
    def render(self):
        if self.i >= self.len: return True
        self.i += 1
        t = self.text[:self.i]
        self.surf = self.font.render(t, True, self.c)
        return False


    def blit(self,screen):
        screen.blit(self.surf, (self.x, self.y))

    def __repr__(self):
        return f"TextBlock(text={self.text}, x={self.x}, y={self.y}, flag={self.flag})"

class Dialogue:
    def __init__(self, text, dimensions, fontsize=24):
        self.fontsize = fontsize
        self.text = text
        self.dimensions = dimensions
        self.dimx = dimensions[0]
        self.dimy = dimensions[1]
        self.font = pygame.font.Font("assets/font.ttf", fontsize)
        self.textsurface = pygame.Surface(self.dimensions, pygame.SRCALPHA)
        self.rendered_text = []  # Stores the progressively rendered TextBlocks
        self.current_index = 0  # Tracks the current letter being rendered
        self.frame_counter = 0  # Frame counter for controlling the scribble speed
        self.scribble_speed = 10  # Frames per letter
        self.text_blocks = self.format_text()  # Preprocess the text into TextBlocks

    def format_text(self):
        words = self.text.split(" ")
        text = []
        cx, cy = 0, 0

        for word in words:
            f = []
            if word.startswith("&"):
                f.append("b")
                word = word[1:]
            if word.startswith("%"):
                f.append("i")
                word = word[1:]
            if word.startswith("_"):
                f.append("u")
                word = word[1:]
            if word.startswith("*"):
                f.append("h")
                word = word[1:]

            # Create a temporary font object to calculate the word width with flags
            temp_font = pygame.font.Font("assets/font.ttf", self.fontsize)
            if 'b' in f:
                temp_font.set_bold(True)
            if 'i' in f:
                temp_font.set_italic(True)
            if 'u' in f:
                temp_font.set_underline(True)

            word_width = temp_font.size(word + " ")[0]

            # Check if adding the word exceeds the line width
            if cx + word_width > self.dimx:
                # Move to the next line
                cx = 0
                cy += self.fontsize

            # Create a TextBlock for the word
            text.append(TextBlock(word, cx, cy, f, self.fontsize))
            cx += word_width  # Update the x position for the next word

        return text

    def update(self):
        self.frame_counter += 1
        if self.current_index < len(self.text_blocks):
            if self.frame_counter >= self.scribble_speed:
                self.frame_counter = 0
                if self.text_blocks[self.current_index].render():
                    self.current_index += 1
            return False
        return True

  # Still rendering text
        self.frame_counter += 1
        if self.frame_counter >= self.scribble_speed and self.current_index < len(self.text_blocks):
            self.rendered_text.append(self.text_blocks[self.current_index])
            self.current_index += 1
            self.frame_counter = 0  # Reset the frame counter
        if self.current_index >= len(self.text_blocks):
            return True  # All text has been rendered
        return False  # Still rendering text

    def render(self):
        self.textsurface.fill((0, 0, 0, 0))  # Clear the surface
        for block in self.text_blocks:
            block.blit(self.textsurface)
        return self.textsurface

    def draw(self, surf):
        surf.blit(self.render(), (32, 48))

class DialogueBox:
    def __init__(self,game,dialogues):
        self.game = game
        self.dialogues = dialogues
        self.dialogue = dialogues[0]
        self.current = 0
        
        self.drawbox()
        self.visible = True

    def drawbox(self):
        self.box = pygame.Surface((832,192), pygame.SRCALPHA)
        self.box.blit(load_image("assets/ui/dialogbox_corner.png",192), (0, 0))
        self.box.blit(load_image("assets/ui/dialogbox_body.png",(448,192)), (192, 0))
        self.box.blit(pygame.transform.flip(load_image("assets/ui/dialogbox_corner.png",192),True,False), (624, 0))


    def draw(self):
        if self.visible:
            self.game.stop = True
            if self.dialogue.update():
                self.next()
            self.dialogue.draw(self.box)
            self.game.window.blit(self.box, (200, 608))

    def next(self):
        keys = pygame.key.get_pressed()
        if True in keys:
            self.current += 1
            if self.current >= len(self.dialogues):
                self.game.uilayer.remove(self)
                self.game.stop = False
            else:
                self.dialogue = self.dialogues[self.current]
                self.drawbox()
            

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
