import pygame

from tkinter import *
import tkinter


class View:
    x: int
    y: int

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.Surface((self.width, self.height))

    def get_screen(self):
        return self.screen

    def draw_map(self, sight_map):
        self.screen.fill((200, 200, 200))
        mlist = [0, 2, 1]
        for n in range(3):  # 行
            for m in mlist:  # 列
                if sight_map[n][m] == 0:
                    if m == 0 or m == 2:
                        self.draw_sidewall(n, m)
                    else:
                        self.draw_centerwall(n, m)
                if sight_map[n][1] == 8 or sight_map[n][1] == 9:
                    self.draw_floor(n, m)

    def draw_sidewall(self, n, m):  # m=0 or 2
        if m == 0:  # 左側
            e = [-1, -3, -7, -11]
        else:  # 右側
            e = [1, 3, 7, 11]
        for a in range(len(e)):
            e[a] = e[a] * self.width / 22
        e1 = e[n]
        e2 = e[n + 1]
        v = [
            [e1, -e1],
            [e1, e1],
            [e2, e2],
            [e2, -e2],
            [e[3], -e2],
            [e[3], e2]
        ]
        for i in range(len(v)):
            v[i][0] = v[i][0] + self.width / 2
            v[i][1] = v[i][1] + self.height / 2
        pygame.draw.polygon(self.screen, (255, 255, 255), v[:4])  # 台形部分
        pygame.draw.polygon(self.screen, (0, 0, 0), v[:4], 1)  # の枠
        pygame.draw.polygon(self.screen, (255, 255, 255), v[2:])  # 長方形部分
        pygame.draw.polygon(self.screen, (0, 0, 0), v[2:], 1)  # の枠

    def draw_centerwall(self, n, m):  # m=1
        e = [3, 7, 11]
        for a in range(len(e)):
            e[a] = e[a] * self.width / 22
        e1 = e[n]
        v = [
            [e1, e1],
            [e1, -e1],
            [-e1, -e1],
            [-e1, e1],
        ]
        for i in range(len(v)):
            v[i][0] = v[i][0] + self.width / 2
            v[i][1] = v[i][1] + self.height / 2
        pygame.draw.polygon(self.screen, (255, 255, 255), v)
        pygame.draw.polygon(self.screen, (0, 0, 0), v, 1)

    def draw_floor(self, n, m):  # 床
        e = [1, 3, 7, 11]
        for a in range(len(e)):
            e[a] = e[a] * self.width / 22
        e1 = e[n]
        e2 = e[n + 1]
        v = [
            [-e1, e1],
            [e1, e1],
            [e2, e2],
            [-e2, e2]
        ]
        for i in range(len(v)):
            v[i][0] = v[i][0] + self.width / 2
            v[i][1] = v[i][1] + self.height / 2
        pygame.draw.polygon(self.screen, (255, 165, 0), v)
        pygame.draw.polygon(self.screen, (0, 0, 0), v, 1)  # 枠

    def draw_arrow(self, arrow):
        font = pygame.font.SysFont("microsoftjhengheimicrosoftjhengheiuibold", 40)
        text = font.render(arrow, False, (255, 0, 0))
        self.screen.blit(text, (self.width / 2, self.height / 4))

    def draw_clear_message(self):
        font = pygame.font.SysFont("comicsansms", 40)
        text = font.render("CLEAR!", False, (255, 0, 0))
        self.screen.blit(text, (self.width / 2 - 80, self.height / 2 - 130))
        text = font.render("Go next floor", False, (255, 0, 0))
        self.screen.blit(text, (self.width / 2 - 140, self.height / 2 - 70))
        text = font.render("with return key", False, (255, 0, 0))
        self.screen.blit(text, (self.width / 2 - 155, self.height / 2 - 10))

    def draw_floor_number(self,number):
        font = pygame.font.SysFont("comicsansms", 40)
        text = font.render(f"{number}F", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 - 10, 20))
