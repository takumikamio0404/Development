"""
神尾 巧
迷路脱出ゲーム
"""

import random
from maze import Maze
from View import View
from Title import Title

import pygame

# import sys


# =====================================================
# MAZE_WIDTH = 31  # 奇数 5以上　迷路の横幅
# MAZE_HEIGHT = 31  # 奇数 5以上　迷路の縦幅

MAZE_SIZES = [11, 21, 31]

VIEW_WIDTH = 500
VIEW_HEIGHT = 500

IMAGE_WIDTH = 500
IMAGE_HEIGHT = 500

CANVAS_WIDTH = IMAGE_WIDTH + VIEW_WIDTH
if IMAGE_HEIGHT < VIEW_HEIGHT:
    CANVAS_HEIGHT = VIEW_HEIGHT
else:
    CANVAS_HEIGHT = IMAGE_HEIGHT

DIFFICULTY = "easy"

LOOP = True
FPS = 60

FACELIST = [[-1, 0], [0, -1], [1, 0], [0, 1]]  # それぞれ下左上右を表す


# =====================================================

class MazeGame:
    height: int
    width: int
    floormap: list
    lights: list
    clear_flag: bool
    floor_number: int
    mode: str

    def __init__(self):
        self.width = MAZE_SIZES[title.get_choice()]
        self.height = MAZE_SIZES[title.get_choice()]
        self.floormap = []
        self.lights = []
        self.player = Player(0, 0)
        self.clear_flag = False
        self.floor_number = 1
        self.mode = "title"
        self.difficulty = "normal"

    def start(self):
        self.set_maze()
        # self.save(r"map.txt")  # ファイルに保存しつつ迷路生成
        # self.game.load(r"map.txt")  # ファイルから読み出し
        # self.print_floormap()
        if self.difficulty == "easy":  # 難易度が簡単なら
            self.explore_root()  # 正しいルートを探索
        self.redraw()  # 画面の書き直し

    def explore_root(self):
        self.explore([self.player.x, self.player.y])
        for i in range(self.width + 2):  # 探索後は通路が4になっているため、1に直す
            for j in range(self.height + 2):
                if self.floormap[i][j] == 4:
                    self.floormap[i][j] = 1

    def explore(self, process):
        for face in FACELIST:  # 上下左右各方向について
            now = self.floormap[process[0]][process[1]]
            after = self.floormap[process[0] + face[0]][process[1] + face[1]]
            if after == 9:
                if now != 8:
                    self.floormap[process[0]][process[1]] = 5
                return True
            elif after == 1:
                self.floormap[process[0] + face[0]][process[1] + face[1]] = 4
                if self.explore([process[0] + face[0], process[1] + face[1]]):
                    if now != 8:
                        self.floormap[process[0]][process[1]] = 5
                    return True
        return False

    def check_lights(self):
        for x in range(self.player.x - 1, self.player.x + 2):
            for y in range(self.player.y - 1, self.player.y + 2):
                self.lights[x][y] = True

    def redraw(self):
        if self.mode == "title":
            title.draw()
            title_screen = title.get_screen()
            screen.blit(title_screen, (0, 0))
            pygame.display.flip()
        elif self.mode == "maze":
            screen.fill((200, 200, 200))
            self.check_lights()
            self.draw_floormap()  # マップを書く
            self.player.draw()  # プレイヤーを書く
            view.draw_map(self.sight())  # 一人称視点の部分を書く
            view.draw_floor_number(self.floor_number)
            if self.difficulty == "easy":
                self.player.correct_direction()
            if self.clear_flag:
                view.draw_clear_message()
            view_screen = view.get_screen()
            screen.blit(view_screen, (IMAGE_WIDTH, 0))
            screen.blit(maze_screen, (0, 0))
            pygame.display.flip()

    def print_floormap(self):  # デバッグ用 現在のフロアマップの様子をコンソールに表示
        for path in self.floormap:
            print(path)

    def set_maze(self):  # 迷路生成
        # マップの外側を1層分の2で囲んでおく
        self.floormap = Maze(self.width, self.height).maze
        self.lights = [[False] * (self.width + 2) for i in range(self.height + 2)]
        for path in self.floormap:
            path.insert(0, 2)
            path.append(2)
        blanks = []
        for a in range(self.width + 2):
            blanks.append(2)
        self.floormap.insert(0, blanks)
        self.floormap.append(blanks)
        # 行き止まりの中からランダムでスタートとゴールをえらんでる
        stops = []
        for i in range(self.height):
            for j in range(self.width):
                if i % 2 == 0 and j % 2 == 0 and self.floormap[i][j] != 2:
                    count = 0
                    for face in FACELIST:
                        if self.floormap[i + face[0]][j + face[1]] == 0:
                            count += 1
                    if count == 3:
                        stops.append([i, j])
        random.shuffle(stops)
        start = stops.pop()
        goal = stops.pop()
        self.player = Player(start[0], start[1])  # プレイヤーをスタート位置に
        self.floormap[start[0]][start[1]] = 8
        self.floormap[goal[0]][goal[1]] = 9

    def save(self, filename):  # 現在のフロアマップをファイル保存
        with open(filename, mode="w") as file:
            for path in self.floormap:
                check = 0
                for cell in path:
                    if cell != 2:  # ファイルの見栄え的な問題で2は排除
                        check = 1
                        file.write(f"{cell}")
                if check == 1:  # 全部空白だったらその行は書かない
                    file.write("\n")

    def load(self, filename):
        blanks = []  # ロードしてくるときに2の膜を張る
        for a in range(self.width + 4):
            blanks.append(2)
        floormap = [blanks, blanks]
        with open(filename) as file:
            for line in file:
                nest = [2, 2]
                for cell in line:
                    if cell != "\n":
                        nest.append(int(cell))
                nest.append(2)
                nest.append(2)
                floormap.append(nest)
            floormap.append(blanks)
            floormap.append(blanks)
        self.floormap = floormap
        self.lights = [[False] * (self.width + 2) for i in range(self.height + 2)]

    def draw_floormap(self):
        cell_size = IMAGE_WIDTH / (self.width + 2)
        font = pygame.font.SysFont("comicsansms", int(cell_size))
        draw.rect(maze_screen, (200, 200, 200), (0, 0, IMAGE_WIDTH, IMAGE_HEIGHT))
        for i in range(len(self.floormap)):
            for j in range(len(self.floormap[i])):
                if self.lights[i][j]:
                    cell = self.floormap[i][j]
                    y, x = cell_size * i, cell_size * j
                    if cell == 5:  # 正しい道はピンク
                        draw.rect(maze_screen, (255, 192, 203), pygame.Rect(x, y, cell_size + 1, cell_size + 1))
                    elif cell == 1:  # 通路は白
                        draw.rect(maze_screen, (255, 255, 255), pygame.Rect(x, y, cell_size + 1, cell_size + 1))
                    elif cell == 0:  # 壁は黒
                        draw.rect(maze_screen, (0, 0, 0), pygame.Rect(x, y, cell_size + 1, cell_size + 1))
                    elif cell == 8:  # スタートはオレンジにS
                        draw.rect(maze_screen, (255, 165, 0), pygame.Rect(x, y, cell_size + 1, cell_size + 1))
                        text = font.render("S", False, (0, 0, 0))
                        maze_screen.blit(text, (x + 3, y - 3))
                    elif cell == 9:  # ゴールはオレンジにG
                        draw.rect(maze_screen, (255, 165, 0), pygame.Rect(x, y, cell_size + 1, cell_size + 1))
                        text = font.render("G", False, (0, 0, 0))
                        maze_screen.blit(text, (x + 4, y - 4))

    def sight(self):  # プレイヤーの立ってる場所も含めた前方9マスをfieldから切り取った3*3入れ子リストを返す、ゴリ押し型
        x = self.player.x
        y = self.player.y
        if self.player.face == 0:  # 上向いてれば
            sight_map = [
                [self.floormap[x - 2][y - 1], self.floormap[x - 2][y], self.floormap[x - 2][y + 1]],
                [self.floormap[x - 1][y - 1], self.floormap[x - 1][y], self.floormap[x - 1][y + 1]],
                [self.floormap[x][y - 1], self.floormap[x][y], self.floormap[x][y + 1]],
            ]
        elif self.player.face == 1:  # 左向いてれば
            sight_map = [
                [self.floormap[x + 1][y - 2], self.floormap[x][y - 2], self.floormap[x - 1][y - 2]],
                [self.floormap[x + 1][y - 1], self.floormap[x][y - 1], self.floormap[x - 1][y - 1]],
                [self.floormap[x + 1][y], self.floormap[x][y], self.floormap[x - 1][y]],
            ]
        elif self.player.face == 2:  # 下向いてれば
            sight_map = [
                [self.floormap[x + 2][y + 1], self.floormap[x + 2][y], self.floormap[x + 2][y - 1]],
                [self.floormap[x + 1][y + 1], self.floormap[x + 1][y], self.floormap[x + 1][y - 1]],
                [self.floormap[x][y + 1], self.floormap[x][y], self.floormap[x][y - 1]],
            ]
        else:  # 右向いてれば
            sight_map = [
                [self.floormap[x - 1][y + 2], self.floormap[x][y + 2], self.floormap[x + 1][y + 2]],
                [self.floormap[x - 1][y + 1], self.floormap[x][y + 1], self.floormap[x + 1][y + 1]],
                [self.floormap[x - 1][y], self.floormap[x][y], self.floormap[x + 1][y]],
            ]
        return sight_map

    def change_difficulty(self):
        if self.difficulty == "normal":
            self.difficulty = "easy"
            self.floormap[self.player.x][self.player.y] = 4
            self.explore_root()
            self.redraw()
        elif self.difficulty == "easy":
            self.difficulty = "normal"
            for i in range(self.width + 2):  # 正しい道をただの道にする
                for j in range(self.height + 2):
                    if self.floormap[i][j] == 5:
                        self.floormap[i][j] = 1
            self.redraw()

    def turn_left(self):
        self.player.face += 1  # プレイヤーの向いてる方向をひとつ左に
        if self.player.face == 4:
            self.player.face = 0
        self.redraw()

    def turn_right(self):
        self.player.face -= 1  # プレイヤーの向いてる方向をひとつ右に
        if self.player.face == -1:
            self.player.face = 3
        self.redraw()

    def go_straight(self):
        self.player.move()
        if self.floormap[self.player.x][self.player.y] == 9:  # ゴールに着いたら
            self.clear_flag = True
            self.redraw()

    def fall_back(self):
        self.player.move(-1)  # バック


class Player:
    x: int
    y: int
    face: int
    coords: list

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.face = 3
        self.coords = [[-1, 0], [0, -1], [1, 0], [0, 1]]

    def move(self, a=1):  # aを-1にするとバックする
        coord_x = self.coords[self.face][0]  # 各向いてる方向に対応する数字を足したり引いたりする
        coord_y = self.coords[self.face][1]
        coord_x = a * coord_x + self.x
        coord_y = a * coord_y + self.y
        front = game.floormap[coord_x][coord_y]  # 正面のマス
        if front != 0 and front != 2:  # 壁か盤面外でなければ
            if front == 8:
                check = 0
                for coord in self.coords:
                    around = game.floormap[self.x + coord[0]][self.y + coord[1]]
                    if around == 5:
                        check = 1
                if check == 0:
                    game.floormap[self.x][self.y] = 1  # 足元を道にする
            elif (front == 5 or front == 9) and game.floormap[self.x][self.y] != 8:
                # 移動先が正しい道かゴールで足元がスタートでなければ
                game.floormap[self.x][self.y] = 1  # 足元を道にする
            self.x = coord_x
            self.y = coord_y  # 移動
            if game.difficulty == "easy" and game.floormap[self.x][self.y] == 1:  # 移動先のマスが道だったら正しい道にする
                game.floormap[self.x][self.y] = 5
            game.redraw()

    def correct_direction(self):  # プレイヤーの周囲の正解の道の方向を示せばゴールへの道を表すことになる
        face = 10
        for i in range(len(self.coords)):
            facecoord = self.coords[i]
            if (game.floormap[self.x + facecoord[0]][self.y + facecoord[1]] == 5  # 正解の道かゴールの方向のインデックスを返す
                    or game.floormap[self.x + facecoord[0]][self.y + facecoord[1]] == 9):
                face = self.face - i  # 向いてる方向と正しい方向を比較する
                break
        if face == 0:
            arrow = "↑"
        elif face == -1 or face == 3:
            arrow = "←"
        elif face == -2 or face == 2:
            arrow = "↓"
        elif face == -3 or face == 1:
            arrow = "→"
        else:
            arrow = ""
        view.draw_arrow(arrow)

    def draw(self):  # この三角がプレイヤーを表す
        cell_size = IMAGE_WIDTH / (game.width + 2)
        v = [[cell_size / 2 - 1, cell_size / 2 - 1], [-cell_size / 2 + 1, cell_size / 2 - 1], [0, -cell_size / 2 + 1]]
        for a in range(self.face):
            for i in range(len(v)):
                t = v[i][0]
                v[i][0] = v[i][1]
                v[i][1] = -t
        for i in range(len(v)):
            v[i][0] += self.y * cell_size + cell_size / 2
            v[i][1] += self.x * cell_size + cell_size / 2
        draw.polygon(maze_screen, (0, 150, 0), v)


# ======================================================================================================================

pygame.init()
screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))

title = Title(CANVAS_WIDTH, CANVAS_HEIGHT)

maze_screen = pygame.Surface((IMAGE_WIDTH, IMAGE_HEIGHT))
maze_screen.fill((200, 200, 200))

view = View(VIEW_WIDTH, VIEW_HEIGHT)

draw = pygame.draw

clock = pygame.time.Clock()

game = MazeGame()
# game.start()
game.redraw()

while LOOP:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            LOOP = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                LOOP = False
            elif game.mode == "title":
                if event.key == pygame.K_RETURN:
                    game.mode = "maze"
                    game.width = MAZE_SIZES[title.get_choice()]
                    game.height = MAZE_SIZES[title.get_choice()]
                    game.start()
                elif event.key == pygame.K_LEFT:
                    title.choose_left()
                    game.redraw()
                elif event.key == pygame.K_RIGHT:
                    title.choose_right()
                    game.redraw()
            elif game.mode == "maze":
                if game.clear_flag:
                    if event.key == pygame.K_RETURN:
                        game.clear_flag = False
                        game.floor_number += 1
                        game.start()
                else:
                    if event.key == pygame.K_LEFT:
                        game.turn_left()
                    elif event.key == pygame.K_RIGHT:
                        game.turn_right()
                    elif event.key == pygame.K_UP:
                        game.go_straight()
                    elif event.key == pygame.K_DOWN:
                        game.fall_back()
                    elif event.key == pygame.K_SPACE:
                        game.change_difficulty()
    clock.tick(FPS)
pygame.quit()
# sys.exit
