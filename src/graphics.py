import time
import pygame
from pygame.locals import *

from gui.gui import *
from network.database import *
from objects import *
from constants import *
import global_vars as g
from utils.utils import countFiles

# gui states
GUI_STATS = 0
GUI_INVENTORY = 1
GUI_EQUIPMENT = 2

class GraphicsEngine():
    ''' class for handling the graphics rendering while ingame (both UI and the game itself) '''

    def __init__(self):
        self.surface = g.gameSurface
        self.surfaceRect = g.gameSurface.get_rect()

        # game surface offset
        self.surfaceRect.top = 16
        self.surfaceRect.left = 16

        # sprites
        self.itemSprites = []
        self.sprites = []

        # surfaces
        self.tileSurface = pygame.image.load(g.dataPath + "/tilesets/Tiles1.png").convert()
        # todo: transparency
        #self.tileSurface.set_colorkey((0, 0, 255))
        self.tileOutlineSurface = pygame.image.load(g.dataPath + "/gui/editor_outline.bmp").convert()
        self.tileOutlineSurface.set_colorkey((255, 0, 204))

        self.fontPlrName = g.systemFont #pygame.font.SysFont(None, 18)
        self.drawMapNameColor = textColor.BRIGHT_RED

        # fringe tiles
        self.tileSurfaceTrans = pygame.image.load(g.dataPath + "/tilesets/Tiles1.png").convert()
        self.tileSurfaceTrans.set_colorkey((0, 0, 0))

        ###############
        # GAME EDITOR #
        ###############
        # tile markers
        # - block
        self.blockSurface = pygame.Surface((PIC_X, PIC_Y))
        self.blockSurface.set_alpha(128)
        self.blockSurface.fill((255, 0, 0))
        font = g.systemFont #pygame.font.SysFont(None, 27)
        markerText = font.render("B", True, (0, 0, 0))
        markerTextRect = markerText.get_rect()
        markerTextRect.centerx = self.blockSurface.get_rect().centerx
        markerTextRect.centery = self.blockSurface.get_rect().centery
        self.blockSurface.blit(markerText, markerTextRect)

        # - warp
        self.warpSurface = pygame.Surface((PIC_X, PIC_Y))
        self.warpSurface.set_alpha(128)
        self.warpSurface.fill((0, 0, 255))
        font = g.systemFont #pygame.font.SysFont(None, 27)
        markerText = font.render("W", True, (255, 255, 255))
        markerTextRect = markerText.get_rect()
        markerTextRect.centerx = self.warpSurface.get_rect().centerx
        markerTextRect.centery = self.warpSurface.get_rect().centery
        self.warpSurface.blit(markerText, markerTextRect)

        # - item
        self.itemSurface = pygame.Surface((PIC_X, PIC_Y))
        self.itemSurface.set_alpha(128)
        self.itemSurface.fill((255, 255, 255))
        font = g.systemFont #pygame.font.SysFont(None, 27)
        markerText = font.render("I", True, (0, 0, 0))
        markerTextRect = markerText.get_rect()
        markerTextRect.centerx = self.itemSurface.get_rect().centerx
        markerTextRect.centery = self.itemSurface.get_rect().centery
        self.itemSurface.blit(markerText, markerTextRect)

        #######
        # GUI #
        #######
        self.gameGUI = GameGUI(self)

        # gui background
        self.backgroundGUI = pygame.image.load(g.dataPath + '/gui/game_background.png')
        g.guiSurface.blit(self.backgroundGUI, (0, 0))

        self.guiState = GUI_STATS

        # initial calls
        self.loadSprites()

    def renderGraphics(self):
        # lower tiles
        for x in range(MAX_MAPX):
            for y in range(MAX_MAPY):
                self.drawMapTile(x, y)

        # items
        for i in range(MAX_MAP_ITEMS):
            if MapItem[i].num is not None:
                self.drawMapItem(i)

        # players
        for i in range(0, len(g.playersOnMap)):
            self.drawPlayer(g.playersOnMap[i])

        # npcs
        #for i in range(0, g.npcHighIndex):
        for i in range(0, MAX_MAP_NPCS):
            self.drawNPC(i)

        # upper tiles
        for x in range(MAX_MAPX):
            for y in range(MAX_MAPY):
                self.drawMapFringeTile(x, y)

        # draw tile outline if in the map editor
        if g.editor == EDITOR_MAP:
            self.drawTileOutline()

        ##################
        # TEXT RENDERING #
        ##################

        for i in range(0, len(g.playersOnMap)):
            self.drawPlayerName(g.playersOnMap[i])

        self.drawMapName(Map.name)

        # draw fps (todo - probably not necessary)
        #if g.boolFPS:
        #    self.drawFPS()

        # draw cursor and player location
        if g.boolLoc:
            self.drawLocation()

        if g.editor == EDITOR_MAP:
            self.drawMapAttributes()

        if DEBUGGING:
            self.drawDebug()

        # dirty hack
        # - the whole thing is rendered in gameGUI so that the GUI is ABOVE the game screen. Stupid stupid hack
        self.gameGUI.draw(self.surface, self.surfaceRect)

    #############
    # FUNCTIONS #
    #############

    def initTileSurface(self, tileset):
        # TODO: THIS IS NOT WORKING ATM
        #self.tileSurface = pygame.image.load("data/tilesets/Tiles1.bmp").convert_alpha()
        #self.tileSurface.set_colorkey((255, 0, 0))
        print "lawl"

    def loadSprites(self):
        # count how many sprites there are
        spriteAmount = countFiles(g.dataPath + '/sprites/')

        # load them all
        for i in range(0, spriteAmount):
            tempImage = pygame.image.load(g.dataPath + "/sprites/" + str(i) + ".bmp").convert()
            tempImage.set_colorkey((0, 0, 0))
            self.sprites.append(tempImage)

         # count how many sprites there are
        itemAmount = countFiles(g.dataPath + '/items/')

        # load them all
        for i in range(0, itemAmount):
            tempImage = pygame.image.load(g.dataPath + "/items/" + str(i) + ".png").convert_alpha()
            self.itemSprites.append(tempImage)

    def drawMapTile(self, x, y):
        if Map.tile[x][y].ground != None:
            self.surface.blit(self.tileSurface, (MapTilePosition[x][y].x, MapTilePosition[x][y].y), (MapTilePosition[x][y].ground))
        else:
            # draw black square
            pygame.draw.rect(self.surface, (0, 0, 0), (MapTilePosition[x][y].x, MapTilePosition[x][y].y, 32, 32))

    def drawMapFringeTile(self, x, y):
        if Map.tile[x][y].fringe != None:
            self.surface.blit(self.tileSurfaceTrans, (MapTilePosition[x][y].x, MapTilePosition[x][y].y), (MapTilePosition[x][y].fringe))

    def drawMapItem(self, itemNum):
        picNum = Item[MapItem[itemNum].num].pic

        if picNum is None:
            return

        x = MapItem[itemNum].x
        y = MapItem[itemNum].y

        self.surface.blit(self.itemSprites[picNum], (MapTilePosition[x][y].x, MapTilePosition[x][y].y))

    def drawSprite(self, sprite, x, y, rect):
        self.surface.blit(self.sprites[sprite], (x, y), rect)

    def drawPlayer(self, index):
        sprite = getPlayerSprite(index)

        tickCount = time.time()

        # check for animation
        anim = 0
        if Player[index].attacking == 0:
            direction = getPlayerDir(index)

            if direction == DIR_UP:
                if Player[index].yOffset < (SIZE_Y/2):
                    anim = 1

            elif direction == DIR_DOWN:
                if Player[index].yOffset < (SIZE_Y/2 * -1):
                    anim = 1

            elif direction == DIR_LEFT:
                if Player[index].xOffset < (SIZE_X/2):
                    anim = 1

            elif direction == DIR_RIGHT:
                if Player[index].xOffset < (SIZE_X/2 * -1):
                    anim = 1

        elif (Player[index].attackTimer + 0.5) > tickCount:
                anim = 2

        # do we want to stop sprite from attacking?
        if (Player[index].attackTimer + 1) < tickCount:
            Player[index].attacking = 0
            Player[index].attackTimer = 0

        # rect(x, y, width, height)
        rect = pygame.Rect((getPlayerDir(index)*3+anim)*32, 0, 32, 32)

        x = getPlayerX(index) * SIZE_X + Player[index].xOffset
        y = getPlayerY(index) * SIZE_Y + Player[index].yOffset - 4

        if y < 0:
            y = 0
            #rect.y = rect.y + (y * -1)

        self.drawSprite(sprite, x, y, rect)

        # todo: draw spell animations

    def drawNPC(self, mapNpcNum):
        if mapNPC[mapNpcNum].num is None:
            return

        tickCount = time.time()

        sprite = NPC[mapNPC[mapNpcNum].num].sprite

        # check for animation
        anim = 0
        if mapNPC[mapNpcNum].attacking == 0:
            direction = mapNPC[mapNpcNum].dir

            if direction == DIR_UP:
                if mapNPC[mapNpcNum].yOffset < (SIZE_Y/2):
                    anim = 1

            elif direction == DIR_DOWN:
                if mapNPC[mapNpcNum].yOffset < (SIZE_Y/2 * -1):
                    anim = 1

            elif direction == DIR_LEFT:
                if mapNPC[mapNpcNum].xOffset < (SIZE_X/2):
                    anim = 1

            elif direction == DIR_RIGHT:
                if mapNPC[mapNpcNum].xOffset < (SIZE_X/2 * -1):
                    anim = 1

        elif (mapNPC[mapNpcNum].attackTimer + 0.5) > tickCount:
            anim = 2

        # do we want to stop sprite from attacking?
        if (mapNPC[mapNpcNum].attackTimer + 1) < tickCount:
            mapNPC[mapNpcNum].attacking = 0
            mapNPC[mapNpcNum].attackTimer = 0

        # rect(x, y, width, height)
        rect = pygame.Rect((mapNPC[mapNpcNum].dir*3+anim)*32, 0, 32, 32)

        x = mapNPC[mapNpcNum].x * SIZE_X + mapNPC[mapNpcNum].xOffset
        y = mapNPC[mapNpcNum].y * SIZE_Y + mapNPC[mapNpcNum].yOffset - 4

        # check if out of bounds because of y offset
        if y < 0:
            y = 0
            #rect.y = rect.y + (y * -1)

        self.drawSprite(sprite, x, y, rect)

        # todo: draw spell animations

    ##################
    # TEXT FUNCTIONS #
    ##################

    def drawText(self, x, y, text, color):
        # shadow
        textSurface = g.nameFont.render(text, 0, (0, 0, 0))
        self.surface.blit(textSurface, (x + 2, y + 2))

        textSurface = g.nameFont.render(text, 0, (0, 0, 0))
        self.surface.blit(textSurface, (x + 1, y + 1))

        # real
        textSurface = g.nameFont.render(text, 0, color)
        self.surface.blit(textSurface, (x, y))

    def drawPlayerName(self, index):
        plrAccess = getPlayerAccess(index)

        if plrAccess == 0:
            color = textColor.BROWN
        elif plrAccess == 1:
            color = textColor.DARK_GREY
        elif plrAccess == 2:
            color = textColor.CYAN
        elif plrAccess == 3:
            color = textColor.BLUE
        elif plrAccess == 4:
            color = textColor.PINK
        else:
            color = textColor.BROWN

        # text length
        textSize = g.nameFont.size(getPlayerName(index))

        # center text
        textX = getPlayerX(index) * PIC_X + Player[index].xOffset + (PIC_X//2) - (textSize[0]/2)
        textY = getPlayerY(index) * PIC_Y + Player[index].yOffset - (PIC_Y//2) - 4

        # make sure text isnt out of screen
        if textY <= 0:
            textY = 0

        if textX <= 0:
            textX = 0

        if textX + textSize[0] >= 480:
            textX = 480 - textSize[0]

        self.drawText(textX, textY, getPlayerName(index), color)

    def drawMapName(self, mapname):
        # todo: determine moral
        textX = (MAX_MAPX + 1) * PIC_X / 2 - ((len(mapname)/2) * 8)
        textY = 1

        self.drawText(textX, textY, mapname, textColor.BRIGHT_RED)

    def drawMapAttributes(self):
        for x in range(MAX_MAPX):
            for y in range(MAX_MAPY):
                tempTile = Map.tile[x][y]

                if tempTile.type == TILE_TYPE_BLOCKED:
                    self.surface.blit(self.blockSurface, (MapTilePosition[x][y].x, MapTilePosition[x][y].y))

                elif tempTile.type == TILE_TYPE_WARP:
                    self.surface.blit(self.warpSurface, (MapTilePosition[x][y].x, MapTilePosition[x][y].y))

                elif tempTile.type == TILE_TYPE_ITEM:
                    self.surface.blit(self.itemSurface, (MapTilePosition[x][y].x, MapTilePosition[x][y].y))

    def drawLocation(self):
        # render text
        self.drawText(10, 10, 'cur x: ' + str(g.cursorXTile) + ' y: ' + str(g.cursorYTile), textColor.YELLOW)
        self.drawText(10, 25, 'loc x: ' + str(getPlayerX(g.myIndex)) + ' y: ' + str(getPlayerY(g.myIndex)), textColor.YELLOW)
        self.drawText(10, 40, ' (map #' + str(getPlayerMap(g.myIndex)) + ')', textColor.YELLOW)

    def drawDebug(self):
        self.drawText(10, 10, "(" + str(getPlayerX(g.myIndex)) + "," + str(getPlayerY(g.myIndex)) + ")", (0, 0, 0))
        self.drawText(10, 25, "HP: " + str(Player[g.myIndex].vitals[0]), (0, 0, 0))
        self.drawText(10, 40, "HP_max: " + str(Player[g.myIndex].maxHP), (0, 0, 0))

    ################
    # GAME EDITORS #
    ################

    def isInBounds(self):
        if self.surfaceRect.collidepoint((g.cursorX, g.cursorY)):
            return True

    def drawTileOutline(self):
        # TODO: Fix the game screen offset problem (-16)
        if not self.isInBounds():
            return

        x = (g.cursorX-16) / PIC_X
        y = (g.cursorY-16) / PIC_Y

        if x >= 0 and x < MAX_MAPX:
            if y >= 0 and y < MAX_MAPY:
                self.surface.blit(self.tileOutlineSurface, (MapTilePosition[x][y].x, MapTilePosition[x][y].y))
