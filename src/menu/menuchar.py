import pygame
from pygame.locals import *
from pgu import gui

import global_vars as g
from constants import *

class characterControl(gui.Table):
    def __init__(self, **params):
        gui.Table.__init__(self, **params)
        self.value = gui.Form()
        self.engine = None

        def btnNextChar(btn):
            self.engine.charIndex += 1
            self.engine.updateCharSelection()

        def btnPrevChar(btn):
            self.engine.charIndex -= 1
            self.engine.updateCharSelection()

        def btnUseChar(btn=None):
            if self.lblPlayerName.value != 'Empty':
                g.tcpConn.sendUseChar(self.engine.charIndex-1)
                g.gameEngine.setState(MENU_INGAME)
            else:
                # new char
                g.tcpConn.sendGetClasses()
                g.gameEngine.setState(MENU_NEWCHAR)

        def btnDelChar(btn):
            print "not yet implemented"

        self.tr()
        self.lblPlayerName = gui.Label('#PLAYER_NAME', antialias=0, color=(255, 0, 0), font=g.charSelFont)
        self.td(self.lblPlayerName, colspan=3, valign=1, align=0)

        self.tr()
        self.lblPlayerExtra = gui.Label('#PLAYER_LEVEL_CLASS', antialias=0, color=(255, 0, 0), font=g.charSelFont, name='lblExtra')
        self.td(self.lblPlayerExtra, colspan=3, align=0)

        self.tr()
        btn = gui.Button("Previous", width=160, height=40)
        btn.connect(gui.CLICK, btnPrevChar, None)
        self.td(btn)
        self.td(gui.Spacer(300, 160))
        btn = gui.Button("Next", width=160, height=40)
        btn.connect(gui.CLICK, btnNextChar, None)
        self.td(btn)

        self.tr()
        self.td(gui.Spacer(0, 0))
        self.btnSelChar = gui.Button("Use Character", width=160, height=30)
        self.btnSelChar.connect(gui.CLICK, btnUseChar, None)
        self.td(self.btnSelChar)
        self.td(gui.Spacer(0, 0))

        self.tr()
        self.td(gui.Spacer(0, 20))

        self.tr()
        self.td(gui.Spacer(0, 0))
        btn = gui.Button("Delete Character", width=160, height=30)
        btn.connect(gui.CLICK, btnDelChar, None)
        self.td(btn)
        self.td(gui.Spacer(0, 0))


class menuCharacters():
    def __init__(self, surface):
        self.surface = surface
        self.backgroundImage = pygame.image.load(g.dataPath + '/gui/menu_background.png')

        # character selection
        self.characters = []
        self.charIndex = 1

        self.charName = ""
        self.charLevel = 0
        self.charClass = "WAAZZOR"
        self.charSprite = 1

        # sprite image
        self.spriteScale = 3
        self.spriteImage = pygame.Surface((PIC_X * self.spriteScale, PIC_Y * self.spriteScale))
        self.spriteImageRect = self.spriteImage.get_rect()
        self.spriteImageRect.centerx = 800/2
        self.spriteImageRect.centery = 600/2

        # GUI
        self.app = gui.App()

        self.charControl = characterControl()
        self.charControl.engine = self

        self.c = gui.Container(align=0, valign=0)
        self.c.add(self.charControl, 0, 0)

        self.app.init(self.c)

    def draw(self):
        # background
        self.surface.blit(self.backgroundImage, (0, 0))
        self.surface.blit(self.spriteImage, self.spriteImageRect)

        self.app.paint()

        pygame.display.update()

    def _handleEvents(self, event):
        # keyboard shortcuts
        self.app.event(event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            g.gameEngine.quitGame()
            #g.gameState = MENU_LOGIN

        elif event.type == KEYDOWN and event.key == K_RETURN:
            self.doUseChar()

    def doUseChar(self):
        if self.charControl.lblPlayerName.value != 'Empty':
            g.tcpConn.sendUseChar(self.charIndex-1)
            g.gameEngine.setState(MENU_INGAME)
        else:
            # new char
            g.tcpConn.sendGetClasses()
            g.gameEngine.setState(MENU_NEWCHAR)


    def updateCharacters(self, data):
        # update character list
        self.characters = data
        self.updateCharSelection()

    def updateCharSelection(self):
        if self.charIndex > MAX_CHARS:
            self.charIndex = 1
        elif self.charIndex < 1:
            self.charIndex = MAX_CHARS

        self.charName   = self.characters[self.charIndex]["charname"]
        self.charLevel  = self.characters[self.charIndex]["charlevel"]
        self.charClass  = self.characters[self.charIndex]["charclass"]
        self.charSprite = self.characters[self.charIndex]["sprite"]

        if self.charName != "":
            self.charControl.lblPlayerName.set_text(self.charName)
            self.charControl.lblPlayerExtra.set_text("Level " + str(self.charLevel) + " " + str(self.charClass))

        else:
            # the character doesnt exist (it's empty)
            self.charControl.lblPlayerName.set_text('Empty')
            self.charControl.lblPlayerExtra.set_text('Create a new character!')

            # todo: change btn text
            #self.charControl.btnSelChar.value = 'New Character'

        self.updateCharSprite(self.charSprite)

    def updateCharSprite(self, sprite):
        tempImage = g.gameEngine.graphicsEngine.sprites[sprite]
        tempSprite = pygame.Surface((32, 32))

        tempSprite.blit(tempImage, (0, 0), (128, 0, 32, 32))

        self.spriteImage = pygame.transform.scale(tempSprite, (PIC_X * self.spriteScale, PIC_Y * self.spriteScale))
        self.spriteImage.set_colorkey((0, 0, 0))
