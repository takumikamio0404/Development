from tkinter import *
import tkinter

import random
from generate import Map
from Window import Window

# ================================================================================================================
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
WIDTH = 20
HEIGHT = 20
CELL_SIZE = 40
X0 = (CANVAS_WIDTH - CELL_SIZE) / (2 * CELL_SIZE)
Y0 = (CANVAS_HEIGHT - CELL_SIZE) / (2 * CELL_SIZE)

TO_NUMBER = {"up": 0, "down": 1, "left": 2, "right": 3}
VECTOR = {"up": [0, -1], "down": [0, 1], "left": [-1, 0], "right": [1, 0]}

MUKI_LIST = ["up", "down", "left", "right"]

ITEMS = ["heal", "arrow", "food", "wand"]

ENEMY_NUM = 3


# ================================================================================================================

class Actor:
    x: int
    y: int
    hp: int
    maxhp: int
    muki: str
    level: int
    power: int
    exp: int
    total_exp: int
    satiety: int
    hunger_count: int
    change_hp: bool
    is_player: bool
    stock_limit: int
    items: list

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.muki = "down"
        self.satiety = 100
        self.hunger_count = 0
        self.change_hp = False
        self.is_player = False
        self.items = []

    def pos_init(self, x, y):
        self.x = x
        self.y = y

    def move(self, destination):
        if destination != "":
            vector = VECTOR[destination]
            after = [0, 0]
            after[0] = self.x + vector[0]
            after[1] = self.y + vector[1]
            self.muki = destination
            after_cell = main.map[after[1]][after[0]]
            # 0=通路,1=壁,2=アイテム,3=階段
            if after_cell != 0 and after_cell != 2 and after_cell != 3:
                return
            # 移動先のマスにプレイヤーがいたら
            if main.player.x == after[0] and main.player.y == after[1]:
                return
            # 移動先のマスに敵がいたら
            for enemy in main.enemys:
                if enemy.x == after[0] and enemy.y == after[1]:
                    return
            self.x = after[0]
            self.y = after[1]
            if after_cell == 2:
                if len(self.items) < self.stock_limit:
                    if self.is_player:
                        main.get_item_count += 1
                    item = random.choice(ITEMS)
                    # print(len(self.items))
                    stock = 1
                    if item == "arrow":
                        stock = 3
                    self.items.append([item, stock])
                    main.map[after[1]][after[0]] = 0
            if self.is_player:
                main.step_count += 1
            if self.is_player and after_cell == 3:
                main.on_stairs = True


class Player(Actor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 100
        self.maxhp = 100
        self.level = 1
        self.power = 35
        self.exp = 0
        self.total_exp = 0
        self.is_player = True
        self.stock_limit = 10

    def draw(self):
        x0 = (X0 + 0.1) * CELL_SIZE
        y0 = (Y0 + 0.1) * CELL_SIZE
        x1 = (X0 + 0.9) * CELL_SIZE
        y1 = (Y0 + 0.9) * CELL_SIZE
        if self.muki == "up":
            canvas.create_polygon([(x0 + x1) / 2, y0, x0, y1, x1, y1], fill="blue")
        elif self.muki == "down":
            canvas.create_polygon([x0, y0, x1, y0, (x0 + x1) / 2, y1], fill="blue")
        elif self.muki == "left":
            canvas.create_polygon([x1, y0, x0, (y0 + y1) / 2, x1, y1], fill="blue")
        elif self.muki == "right":
            canvas.create_polygon([x0, y0, x1, (y0 + y1) / 2, x0, y1], fill="blue")
        if self.change_hp:
            canvas.create_line([X0 * CELL_SIZE, (Y0 + 0.2) * CELL_SIZE,
                                (X0 + self.hp / self.maxhp) * CELL_SIZE, (Y0 + 0.2) * CELL_SIZE], width=5)
            self.change_hp = False

    def attack(self):
        vector = VECTOR[self.muki]
        for enemy in main.enemys:
            if enemy.x == self.x + vector[0] and enemy.y == self.y + vector[1]:
                enemy.damage(self.power)

    def damage(self, enemy_power):
        self.hp -= enemy_power
        main.taken_damege += enemy_power
        if self.hp <= 0:
            main.game_over_cause = "attack"
            main.is_game_over = True
        else:
            self.change_hp = True

    def gain_exp(self, exp):
        self.exp += exp
        self.total_exp += exp
        while True:
            if self.exp >= 10 * 1.1 ** (self.level - 1):
                self.exp -= round(10 * 1.1 ** (self.level - 1))
                self.level += 1
                self.power += 1
                self.maxhp += 1
            else:
                break

    # overwrite
    def move(self, destination):
        super().move(destination)
        if self.satiety > 0:
            if self.hp + round(self.maxhp / 200) < self.maxhp:
                self.hp += round(self.maxhp / 200)
            else:
                self.hp = self.maxhp
            self.hunger_count += 1
            if self.hunger_count == 1:
                self.hunger_count = 0
                self.satiety -= 1
        else:
            self.hp -= 1
            if self.hp <= 0:
                main.game_over_cause = "hunger"
                main.is_game_over = True


class Enemy(Actor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.maxhp = int(100 - 80 * (1 / 2) ** main.floor)
        self.hp = self.maxhp
        self.level = 1
        self.power = 15 + 5 * main.floor
        self.exp = 0
        self.dropexp = 10 + 5 * main.floor
        self.is_enemy = True
        self.stock_limit = 1

    def draw(self):
        x0 = (self.x - main.player.x + X0) * CELL_SIZE
        y0 = (self.y - main.player.y + Y0) * CELL_SIZE
        x1 = (self.x - main.player.x + X0 + 1) * CELL_SIZE
        y1 = (self.y - main.player.y + Y0 + 1) * CELL_SIZE
        if self.muki == "up":
            canvas.create_polygon([(x0 + x1) / 2, y0, x0, y1, x1, y1], fill="red")
        elif self.muki == "down":
            canvas.create_polygon([x0, y0, x1, y0, (x0 + x1) / 2, y1], fill="red")
        elif self.muki == "left":
            canvas.create_polygon([x1, y0, x0, (y0 + y1) / 2, x1, y1], fill="red")
        elif self.muki == "right":
            canvas.create_polygon([x0, y0, x1, (y0 + y1) / 2, x0, y1], fill="red")
        if self.change_hp:
            canvas.create_line(
                [(self.x - main.player.x + X0) * CELL_SIZE, (self.y - main.player.y + Y0 + 0.1) * CELL_SIZE,
                 (self.x - main.player.x + X0 + self.hp / self.maxhp) * CELL_SIZE,
                 (self.y - main.player.y + Y0 + 0.1) * CELL_SIZE], width=5)
            self.change_hp = False

    def attack(self):
        exist = False
        for y in range(self.y - 1, self.y + 2):
            for x in range(self.x - 1, self.x + 2):
                if main.player.x == x and main.player.y == y:
                    exist = True
        if exist:
            main.player.damage(self.power)

    def damage(self, player_power):
        self.hp -= player_power
        if self.hp <= 0:
            main.defeat_count += 1
            if len(self.items) > 0 and main.map[self.y][self.x] != 3:
                main.map[self.y][self.x] = 2
            main.player.gain_exp(self.dropexp)
            place = choice_init_pos(self.x, self.y)
            self.__init__(place[0], place[1])
        else:
            self.change_hp = True


class Main:
    floor: int
    main_map: Map
    map: list
    player: Player
    enemys: list
    map_items: list
    is_title: bool
    on_stairs: bool
    is_game_over: bool
    in_inventory: bool
    game_over_cause: str
    step_count: int
    defeat_count: int
    taken_damege: int
    get_item_count: int

    def start(self):
        self.floor = 1
        self.main_map = Map(WIDTH, HEIGHT)
        init_places = self.main_map.init_map()
        self.map = self.main_map.get_map()
        place = init_places.pop()
        self.player = Player(place[0], place[1])
        self.enemys = []
        for i in range(ENEMY_NUM):
            place = init_places.pop()
            self.enemys.append(Enemy(place[0], place[1]))
        self.on_stairs = False
        self.is_game_over = False
        self.in_inventory = False
        main.game_over_cause = ""
        self.is_title = True
        self.step_count=0
        self.defeat_count=0
        self.taken_damege=0
        self.get_item_count=0
        self.draw()

    def floor_down(self):
        self.floor += 1
        init_places = self.main_map.init_map()
        self.map = self.main_map.get_map()
        place = init_places.pop()
        self.player.pos_init(place[0], place[1])
        self.enemys = []
        for i in range(ENEMY_NUM):
            place = init_places.pop()
            self.enemys.append(Enemy(place[0], place[1]))

    def draw(self):
        canvas.delete("all")
        if self.is_title:
            canvas.create_text(250, 200, text="RogueLike", font=('Times', 30))
            canvas.create_text(250, 280, text="Press any key to start", font=('Times', 15))
            return
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] == 1:  # 壁
                    canvas.create_rectangle([(x - self.player.x + X0) * CELL_SIZE, (y - self.player.y + Y0) * CELL_SIZE,
                                             (x - self.player.x + X0 + 1) * CELL_SIZE,
                                             (y - self.player.y + Y0 + 1) * CELL_SIZE],
                                            fill="green")
                if self.map[y][x] == 2:  # アイテム
                    canvas.create_oval(
                        [(x - self.player.x + X0 + 0.2) * CELL_SIZE, (y - self.player.y + Y0 + 0.2) * CELL_SIZE,
                         (x - self.player.x + X0 + 0.8) * CELL_SIZE, (y - self.player.y + Y0 + 0.8) * CELL_SIZE],
                        fill="yellow")
                if self.map[y][x] == 3:  # 階段
                    canvas.create_rectangle([(x - self.player.x + X0) * CELL_SIZE, (y - self.player.y + Y0) * CELL_SIZE,
                                             (x - self.player.x + X0 + 1) * CELL_SIZE,
                                             (y - self.player.y + Y0 + 1) * CELL_SIZE],
                                            fill="black")
        self.player.draw()
        for enemy in self.enemys:
            enemy.draw()
        if self.in_inventory:
            window.inventory(self.player, self.floor)
        elif self.is_game_over:
            window.game_over(self.game_over_cause, self.floor, self.player.level, self.step_count,
                             self.defeat_count, self.taken_damege, self.get_item_count)
        elif self.on_stairs:
            window.floor_down_choice()

    def key_press(self, event):
        key = event.keysym
        if key == "Escape":
            tk.destroy()
            return 0
        if self.is_title:
            self.is_title = False
            self.draw()
        elif self.is_game_over:
            if key == "z" or key == "Return":
                self.start()
        elif self.in_inventory:
            if key == "x":
                self.in_inventory = False
            elif key == "Left":
                window.move_cursor("left")
            elif key == "Right":
                window.move_cursor("right")
            elif key == "z" or key == "Return":
                item = window.choose_item()
                self.use_item(item)
            self.draw()
        elif self.on_stairs:
            if key == "Left":
                window.change_choice()
            elif key == "Right":
                window.change_choice()
            elif key == "z" or key == "Return":
                self.on_stairs = False
                if window.is_floor_down():
                    self.floor_down()
            self.draw()
        else:
            if key == "w" or key == "a" or key == "s" or key == "d":
                if key == "w":
                    self.player.muki = "up"
                elif key == "s":
                    self.player.muki = "down"
                elif key == "a":
                    self.player.muki = "left"
                elif key == "d":
                    self.player.muki = "right"
                self.draw()
                return 0
            elif key == "z":
                self.player.attack()
            elif key == "x":
                self.in_inventory = True
                self.draw()
                return 0
            elif key == "Up":
                self.player.move("up")
            elif key == "Down":
                self.player.move("down")
            elif key == "Left":
                self.player.move("left")
            elif key == "Right":
                self.player.move("right")
            elif key == "space":
                self.player.move("")
            else:
                return 0
            self.enemy_turn()
            self.draw()

    def enemy_turn(self):
        for enemy in self.enemys:
            check = False
            # 届く範囲にプレイヤーがいたら攻撃
            for muki in MUKI_LIST:
                vector = VECTOR[muki]
                if enemy.x + vector[0] == self.player.x and enemy.y + vector[1] == self.player.y:
                    enemy.muki = muki
                    enemy.attack()
                    check = True
                    break
            if not check:  # 移動
                # 視界の範囲内にプレイヤーがいるかどうか
                for y in range(enemy.y - 3, enemy.y + 4):
                    for x in range(enemy.x - 3, enemy.x + 4):
                        if x == self.player.x and y == self.player.y:
                            check = True
                if check:  # いれば
                    # 幅優先探索でプレイヤーがいる方に進む
                    # プレイヤーとの間に壁があればランダムウォーク

                    # 敵の視界(敵を中心に7*7)を表すリスト
                    # 0が通路、1が壁、2が探索済み通路、8がプレーヤーの位置
                    enemy_sight = []
                    for y in range(enemy.y - 3, enemy.y + 4):
                        line = []
                        for x in range(enemy.x - 3, enemy.x + 4):
                            # 画面外なら
                            if 0 <= x < len(self.map[0]) and 0 <= y < len(self.map):
                                if x == self.player.x and y == self.player.y:
                                    line.append(8)
                                elif self.map[y][x] == 1:
                                    line.append(1)
                                else:
                                    line.append(0)
                            else:
                                line.append(1)
                        enemy_sight.append(line)
                    # 敵がいる位置は壁にする
                    for wall_enemy in self.enemys:
                        if enemy.x - 3 <= wall_enemy.x <= enemy.x + 3 and enemy.y - 3 <= wall_enemy.y <= enemy.y + 3:
                            enemy_sight[wall_enemy.y - enemy.y + 3][wall_enemy.x - enemy.x + 3] = 1

                    # キューには探索するセルの座標と最初に曲がった方向をまとめたものを入れている
                    go_muki = ""
                    queue = [[3, 3, ""]]
                    while len(queue) != 0:
                        cell = queue.pop(0)
                        enemy_sight[cell[1]][cell[0]] = 2
                        for muki in MUKI_LIST:
                            vector = VECTOR[muki]
                            # 画面外なら
                            if not (0 <= (cell[0] + vector[0]) <= 6 and 0 <= (cell[1] + vector[1]) <= 6):
                                continue
                            after_cell = enemy_sight[cell[1] + vector[1]][cell[0] + vector[0]]
                            if after_cell == 8:
                                go_muki = cell[2]
                                break
                            elif after_cell == 0:
                                if cell[2] == "":
                                    queue.append([cell[0] + vector[0], cell[1] + vector[1], muki])
                                else:
                                    queue.append([cell[0] + vector[0], cell[1] + vector[1], cell[2]])
                        if go_muki != "":
                            break
                    # プレイヤーとの間に壁がある場合などは最終的な進行方向は定まらないのでランダムウォークにしている
                    if go_muki == "":
                        go_muki = random.choice(["up", "down", "left", "right"])
                    enemy.move(go_muki)
                else:  # いなければ
                    # ランダムに歩く
                    choice = random.choice(["up", "down", "left", "right"])
                    enemy.move(choice)

    def use_item(self, item):
        if item == "heal":
            if self.player.maxhp - self.player.hp < 50:
                self.player.hp = self.player.maxhp
            else:
                self.player.hp += 50
        elif item == "food":
            if 100 - self.player.satiety < 20:
                self.player.satiety = 100
            else:
                self.player.satiety += 20
        elif item == "arrow":
            self.in_inventory = False
            vector = VECTOR[self.player.muki]
            break_flag = False
            for i in range(1, 6):
                after = [self.player.x + vector[0] * i, self.player.y + vector[1] * i]
                if self.map[after[1]][after[0]] == 1:
                    break
                for enemy in self.enemys:
                    if enemy.x == after[0] and enemy.y == after[1]:
                        enemy.damage(15)
                        break_flag = True
                        break
                if break_flag:
                    break
        elif item == "wand":
            self.in_inventory = False
            vector = VECTOR[self.player.muki]
            break_flag = False
            for i in range(1, 6):
                after = [self.player.x + vector[0] * i, self.player.y + vector[1] * i]
                if self.map[after[1]][after[0]] == 1:
                    break
                for enemy in self.enemys:
                    if enemy.x == after[0] and enemy.y == after[1]:
                        place = choice_init_pos(enemy.x, enemy.y)
                        enemy.pos_init(place[0], place[1])
                        break_flag = True
                        break
                if break_flag:
                    break


def choice_init_pos(enemy_x, enemy_y):
    init_pos_list = main.main_map.room_pos_list(enemy_x, enemy_y)
    while True:
        place = init_pos_list.pop()
        check = True
        for enemy in main.enemys:
            if enemy.x == place[0] and enemy.y == place[1]:
                check = False
                break
        if main.player.x == place[0] and main.player.y == place[1]:
            check = False
        if check:
            break
    return place


tk = tkinter.Tk()
canvas = Canvas(tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack()

window = Window(canvas)

main = Main()
main.start()
tk.bind("<KeyPress>", main.key_press)

tk.mainloop()
