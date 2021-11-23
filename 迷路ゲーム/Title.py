import pygame


class Title:
    width: int
    height: int
    choice: int

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.choice = 1
        self.screen = pygame.Surface((self.width, self.height))

    def get_choice(self):
        return self.choice

    def get_screen(self):
        return self.screen

    def draw(self):
        self.screen.fill((200, 200, 200))
        # pygame.draw.line(self.screen,(0,0,0),[self.width/2,0],[self.width/2,self.height])

        font = pygame.font.SysFont("comicsansms", 50)
        text = font.render("Maze Game", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 - 135, self.height / 2 - 130))

        font = pygame.font.SysFont("comicsansms", 40)
        text = font.render("maze size", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 - 100, self.height / 2 + 20))

        font = pygame.font.SysFont("comicsansms", 30)
        text = font.render("small", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 - 180, self.height / 2 + 90))
        text = font.render("medium", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 - 50, self.height / 2 + 90))
        text = font.render("big", False, (0, 0, 0))
        self.screen.blit(text, (self.width / 2 + 120, self.height / 2 + 90))

        if self.choice==0:
            self.draw_cursor(self.width / 2 - 190, self.height / 2 + 105)
        elif self.choice==1:
            self.draw_cursor(self.width / 2 - 60, self.height / 2 + 105)
        elif self.choice==2:
            self.draw_cursor(self.width / 2 + 110, self.height / 2 + 105)

    def draw_cursor(self,x,y):
        v = [
            [x - 20, y],
            [x - 20, y + 20],
            [x, y + 10]
        ]
        pygame.draw.polygon(self.screen, (0, 0, 0), v)

    def choose_right(self):
        if self.choice != 2:
            self.choice += 1
        else:
            self.choice = 0

    def choose_left(self):
        if self.choice != 0:
            self.choice -= 1
        else:
            self.choice = 2
