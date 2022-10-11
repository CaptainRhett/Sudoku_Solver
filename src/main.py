'''
Auther: Captain Rhett
Date: 2022-10-18 04:53:30
LastEditors: Captain Rhett
LastEditTime: 2022-10-18 05:04:36
'''
from calendar import c
import os

import sys
from turtle import width

import pygame
from pygame import font
from pygame.constants import MOUSEBUTTONDOWN, MOUSEMOTION
from copy import deepcopy

width ,height = 765,765
offH,offW =0,0
class Color:
    # 自定义颜色
    ACHIEVEMENT = (220, 160, 87)
    VERSION = (220, 160, 87)

    # 固定颜色
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (128, 128, 128)  # 中性灰
    TRANSPARENT = (255, 255, 255, 0)  # 白色的完全透明


class Text:
    def __init__(self, text: str, text_color: Color, font_type: str, font_size: int):
        """
        text: 文本内容，如'大学生模拟器'，注意是字符串形式
        text_color: 字体颜色，如Color.WHITE、COLOR.BLACK
        font_type: 字体文件(.ttc)，如'msyh.ttc'，注意是字符串形式
        font_size: 字体大小，如20、10
        """
        self.text = text
        self.text_color = text_color
        self.font_type = font_type
        self.font_size = font_size

        font = pygame.font.Font(os.path.join('font', (self.font_type)), self.font_size)
        self.text_image = font.render(self.text, True, self.text_color).convert_alpha()

        self.text_width = self.text_image.get_width()
        self.text_height = self.text_image.get_height()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        """
        surface: 文本放置的表面
        center_x, center_y: 文本放置在表面的<中心坐标>
        """
        upperleft_x = center_x - self.text_width / 2
        upperleft_y = center_y - self.text_height / 2
        surface.blit(self.text_image, (upperleft_x, upperleft_y))


class Image:
    def __init__(self, img_name: str, ratio=0.4):
        """
        img_name: 图片文件名，如'background.jpg'、'ink.png',注意为字符串
        ratio: 图片缩放比例，与主屏幕相适应，默认值为0.4
        """
        self.img_name = img_name
        self.ratio = ratio

        self.image_1080x1920 = pygame.image.load(os.path.join('image', self.img_name)).convert_alpha()
        self.img_width = self.image_1080x1920.get_width()
        self.img_height = self.image_1080x1920.get_height()

        self.size_scaled = self.img_width * self.ratio, self.img_height * self.ratio

        self.image_scaled = pygame.transform.smoothscale(self.image_1080x1920, self.size_scaled)
        self.img_width_scaled = self.image_scaled.get_width()
        self.img_height_scaled = self.image_scaled.get_height()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        """
        surface: 图片放置的表面
        center_x, center_y: 图片放置在表面的<中心坐标>
        """
        upperleft_x = center_x - self.img_width_scaled / 2
        upperleft_y = center_y - self.img_height_scaled / 2
        surface.blit(self.image_scaled, (upperleft_x, upperleft_y))


class ColorSurface:
    def __init__(self, color, width, height):
        self.color = color
        self.width = width
        self.height = height

        self.color_image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.color_image.fill(self.color)

    def draw(self, surface: pygame.Surface, center_x, center_y):
        upperleft_x = center_x - self.width / 2
        upperleft_y = center_y - self.height / 2
        surface.blit(self.color_image, (upperleft_x, upperleft_y))


class ButtonText(Text):
    def __init__(self, text: str, text_color: Color, font_type: str, font_size: int):
        super().__init__(text, text_color, font_type, font_size)
        self.rect = self.text_image.get_rect()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        super().draw(surface, center_x, center_y)
        self.rect.center = center_x, center_y

    def handle_event(self, command):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.hovered:
            command()


class ButtonImage(Image):
    def __init__(self, img_name: str, ratio=0.4):
        super().__init__(img_name, ratio)
        self.rect = self.image_scaled.get_rect()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        super().draw(surface, center_x, center_y)
        self.rect.center = center_x, center_y

    def handle_event(self, command):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.hovered:
            command()


class ButtonColorSurface(ColorSurface):
    def __init__(self, color, width, height):
        super().__init__(color, width, height)
        self.rect = self.color_image.get_rect()

    def draw(self, surface: pygame.Surface, center_x, center_y):
        super().draw(surface, center_x, center_y)
        self.rect.center = center_x, center_y

    def handle_event(self, command, *args):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.hovered:
            command(*args)


class Box:
    def __init__(self):
        self.cells = []


class Board:
    def __init__(self):
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.boxes = [Box() for _ in range(9)]
        self.lines = [Line() for _ in range(18)]

        for h_Index in range(9):
            for w_Index in range(9):
                box_Index = int(w_Index / 3) + 3 * int(h_Index / 3)
                verticalLineIndex = w_Index
                horizontalLineIndex = h_Index + 9
                newCell = Cell(self.boxes[box_Index], self.lines[verticalLineIndex],
                               self.lines[horizontalLineIndex], (h_Index, w_Index))
                self.cells[h_Index][w_Index] = newCell
                self.boxes[box_Index].cells.append(newCell)
                self.lines[verticalLineIndex].cells.append(newCell)
                self.lines[horizontalLineIndex].cells.append(newCell)

    def isValid(self, what, where, values):
        cellInQuestion = self.cells[where[0]][where[1]]
        return cellInQuestion.isValid(what, values)

    def solve(self, values):
        global stop
        global boardToDraw
        if stop:
            return None
        boardToDraw = values
        checkInput()
        
        

        firstUnsolvedAddress = (-1, -1)

        for i in range(9):
            for j in range(9):
                if values[i][j] == 0:
                    firstUnsolvedAddress = (i, j)
                    break
            if firstUnsolvedAddress[0] != -1:
                break

        if firstUnsolvedAddress[0] == -1:
            return values

        for valueToTry in range(1, 10):
            if self.isValid(valueToTry, firstUnsolvedAddress, values):
                newValues = deepcopy(values)
                newValues[firstUnsolvedAddress[0]][firstUnsolvedAddress[1]] = valueToTry
                colourCell((125,125,125),firstUnsolvedAddress)
                result = self.solve(newValues)
                if result:
                    return result

        return None


class Cell:
    def __init__(self, box, lineV, lineH, pos):
        self.box = box
        self.lineV = lineV
        self.lineH = lineH
        self.pos = pos

    def isValid(self, what, values):
        for neighCell in self.box.cells:
            if what == values[neighCell.pos[0]][neighCell.pos[1]]:
                return False
        for neighCell in self.lineV.cells:
            if what == values[neighCell.pos[0]][neighCell.pos[1]]:
                return False
        for neighCell in self.lineH.cells:
            if what == values[neighCell.pos[0]][neighCell.pos[1]]:
                return False
        return True


class Line:
    def __init__(self):
        self.cells = []


def checkInput():
    global white
    global black
    global boardToDraw
    global selectedSpace
    global highlight
    global valuesOnTheBoard
    global gameBoard
    global stop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                white, black = black, white
            if event.key == pygame.K_r:
                valuesOnTheBoard = [[0 for _ in range(9)] for _ in range(9)]
                boardToDraw = valuesOnTheBoard
                stop = True
            if event.key == pygame.K_SPACE:
                stop = False
                gameBoard.solve(valuesOnTheBoard)
                highlight = None

            if (event.key == pygame.K_1 or event.key == pygame.K_KP1) and selectedSpace != (-1, -1):
                if gameBoard.isValid(1, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 1
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_2 or event.key == pygame.K_KP2) and selectedSpace != (-1, -1):
                if gameBoard.isValid(2, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 2
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_3 or event.key == pygame.K_KP3) and selectedSpace != (-1, -1):
                if gameBoard.isValid(3, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 3
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_4 or event.key == pygame.K_KP4) and selectedSpace != (-1, -1):
                if gameBoard.isValid(4, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 4
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_5 or event.key == pygame.K_KP5) and selectedSpace != (-1, -1):
                if gameBoard.isValid(5, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 5
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_6 or event.key == pygame.K_KP6) and selectedSpace != (-1, -1):
                if gameBoard.isValid(6, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 6
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_7 or event.key == pygame.K_KP7) and selectedSpace != (-1, -1):
                if gameBoard.isValid(7, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 7
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_8 or event.key == pygame.K_KP8) and selectedSpace != (-1, -1):
                if gameBoard.isValid(8, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 8
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)
            if (event.key == pygame.K_9 or event.key == pygame.K_KP9) and selectedSpace != (-1, -1):
                if gameBoard.isValid(9, selectedSpace, valuesOnTheBoard):
                    valuesOnTheBoard[selectedSpace[0]][selectedSpace[1]] = 9
                    boardToDraw = valuesOnTheBoard
                    selectedSpace = (-1, -1)
                    highlight = None
                else:
                    flashCell(selectedSpace)

        if event.type == pygame.MOUSEBUTTONUP:
            stop = True
            boardToDraw = valuesOnTheBoard
            selectedSpace = getCellCoordsForScreenCoords(event.pos)
            colourCell(Color.GREEN, selectedSpace)


def colourCell(withColour, cell):
    global offH
    global offW
    global highlight
    global highlightColour

    cellWidth = int(width / 9)

    highlight = pygame.Rect(offW + cell[1] * cellWidth, offH + cell[0] * cellWidth, cellWidth, cellWidth)
    highlightColour = withColour


def flashCell(cellNumber):
    for i in range(5):
        colourCell(Color.RED, cellNumber)
        drawBoard(scene)
        pygame.time.wait(10)
        colourCell(white, cellNumber)
        drawBoard(scene)
        pygame.time.wait(10)
    colourCell(Color.GREEN, cellNumber)
    drawBoard(scene)

def drawBoard(scene):
    global offW
    global offH
    size,screen = scene.basic_background()

    screen.fill(white)

    maxW = int(width / 9) * 9
    maxH = int(height / 9) * 9
    offW = int((width - maxW) / 2)
    offH = int((height - maxH) / 2)
    


    if highlight:
        pygame.draw.rect(screen, highlightColour, highlight)

    for i in range(0, 10):
        if i % 3 == 0:
            intensity = 3
        else:
            intensity = 1
        pygame.draw.line(screen, black, (offW + int(width / 9) * i, offH), (offW + int(width / 9) * i, offH + maxH),
                         intensity)
        pygame.draw.line(screen, black, (offW, offH + int(height / 9) * i), (offW + maxW, offH + int(height / 9) * i),
                         intensity)


    myfont = pygame.font.Font((os.path.join('font', 'myfont.ttf')), int(0.1 * height))

    for i in range(9):
        for j in range(9):
            if str(boardToDraw[i][j]) == "0":
                charToDraw = ""
            else:
                charToDraw = str(boardToDraw[i][j])
            label = myfont.render(charToDraw, 1, black)
            screen.blit(label, getScreenCoordsForCell((i, j)))

    pygame.display.flip()

def getCellCoordsForScreenCoords(pos):
    global offH
    global offW
    cellWidth = int(width / 9)

    x = int((pos[1] - offW) / cellWidth)
    y = int((pos[0] - offH) / cellWidth)

    return x, y


def getScreenCoordsForCell(cellPos):
    global offH
    global offW
    cellWidth = int(width / 9)

    x = offH + cellWidth * cellPos[1] + int(cellWidth / 5)
    y = offW + cellWidth * cellPos[0] + int(cellWidth / 9)

    return x, y


class InterFace():
    def __init__(self):
        pygame.init()

    def basic_background(self):
        """
        <基本背景><basic_background>\n
        返回值为背景尺寸和背景表面
        """
        # 设置logo和界面标题
        game_icon = pygame.image.load(os.path.join('image', 'icon.png'))
        game_caption = 'Sukodu Solver'
        pygame.display.set_icon(game_icon)
        pygame.display.set_caption(game_caption)

        # 设置开始界面
        
        size = width, height 
        screen = pygame.display.set_mode(size)
        screen.fill(Color.WHITE)
        # 设置背景贴图
        Image('background.png',ratio=0.2).draw(screen, width /2, 1*height/3 )

        return size, screen

    def start_interface(self):
        #  set basic background
        size, screen = self.basic_background()
        width, height = size

        # 设置<开始界面>文字和贴图
        Image('ink.png', ratio=0.4).draw(screen, width * 0.5, height * 0.67)  # 墨印
        
        Text('Sukodu Solver', Color.RED, 'HYHanHeiW.ttf', 50).draw(screen, width / 2, height * 1 / 3)  # name 
        Text('By CaptainRhett', Color.VERSION, 'msyh.ttc', 12).draw(screen, width / 2, height * 0.97)  # auther
        

        button_start = ButtonText('Go', Color.WHITE, 'msyh.ttc', 23)  
        button_start.draw(screen, width / 2, height * 2 / 3)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # ！此处为界面切换的关键，即进入另一死循环
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button_start.handle_event(self.second_interface)

            pygame.display.update()
    def second_interface(self):
        """
        <开始界面><start_interface>
        """
        # 设置<基本背景>
        size, screen = self.basic_background()
        width, height = size
        screen.fill(Color.WHITE) 
        Image('ink.png', ratio=0.4).draw(screen, width * 0.66, height * 0.75)

        button_solve =ButtonText('Begin',Color.WHITE,'msyh.ttc',23)
        button_solve.draw(screen, width *0.66, height * 0.75)
       
        Text('How to use', Color.BLACK, 'HYHanHeiW.ttf', 50).draw(screen, 1*width/3, height * 1 / 6)
        Text('Move mose and scrolling its wheel to choose a blank', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.35)
        Text('Put numbers into the grid via keyboard', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.4)
        Text('Press Space to solve', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height*0.45 )
        Text('Press D to swift day/night mode', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.5)
        Text('Press R to clear the grid', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.55)
        Text('If the program dose not work', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.6)
        Text('Try to press more times', Color.BLACK, 'HYHanHeiW.ttf', 25).draw(screen, width*0.5, height * 0.65)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
               
                if event.type == pygame.MOUSEBUTTONDOWN:
                    button_solve.handle_event(self.solver_interface)

            pygame.display.update()
    # solver interface
    def solver_interface(self):
       
        
        size, screen = self.basic_background()
        width, height = size
        
    
        
        button_back = ButtonColorSurface(Color.TRANSPARENT, 26, 26)
        button_back.draw(screen, width * 0.07, height * 0.047)
        

        while True:
            checkInput()
            screen.fill(white)

            maxW = int(width / 9) * 9
            maxH = int(height / 9) * 9
            offW = int((width - maxW) / 2)
            offH = int((height - maxH) / 2)
            


            if highlight:
                pygame.draw.rect(screen, highlightColour, highlight)

            for i in range(0, 10):
                if i % 3 == 0:
                    intensity = 3
                else:
                    intensity = 1
                pygame.draw.line(screen, black, (offW + int(width / 9) * i, offH), (offW + int(width / 9) * i, offH + maxH),
                                intensity)
                pygame.draw.line(screen, black, (offW, offH + int(height / 9) * i), (offW + maxW, offH + int(height / 9) * i),
                                intensity)
            myfont = pygame.font.Font((os.path.join('font', 'myfont.ttf')), int(0.1 * height))

            for i in range(9):
                for j in range(9):
                    if str(boardToDraw[i][j]) == "0":
                        charToDraw = ""
                    else:
                        charToDraw = str(boardToDraw[i][j])
                    label = myfont.render(charToDraw, 1, black)
                    screen.blit(label, getScreenCoordsForCell((i, j)))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    button_back.handle_event(self.start_interface)

            pygame.display.update()


if __name__ == '__main__':
    gameBoard = Board()
    valuesOnTheBoard = [[0 for _ in range(9)] for _ in range(9)]
    boardToDraw = valuesOnTheBoard
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    
    highlight = None
    stop = False
    scene = InterFace()
    scene.start_interface()
