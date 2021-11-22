"""
神尾 巧
マインスイーパー
"""
import random
from dataclasses import dataclass
from texture import Texture
from tkinter import *
import tkinter

# ----------------------------------------------------------------------------------------------------------------------
FIELDSIZE_DICT = {20: "大", 10: "中", 5: "小"}
TEXTURE_DICT = {"minecraft": "マインクラフト", "normal": "ノーマル"}
GAMEMODE_DICT = {"classic": "クラシック", "item": "アイテム"}


# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class Cell:
    def __init__(self, i, j, state, bomb):
        self.row = i
        self.line = j
        self.x = 24 + j * 32
        self.y = 24 + i * 32
        self.state = state
        self.bomb = bomb


@dataclass
class Box:
    field_width: int
    field_height: int
    number_of_bomb: int
    rest_dynamite: int
    rest_map: int
    rest_shuffle: int
    field: list
    rock: int
    rock_text_id: id
    now_gamemode_id: id
    now_texture_id: id
    now_fieldsize_id: id
    rest_dynamite_id: id
    rest_map_id: id
    rest_shuffle_id: id
    gamemode: str
    is_btn_small: bool
    on_dynamite: bool
    on_map: bool
    btn_continue: Button
    btn_stop: Button
    btn_start: Button
    btn_back: Button
    btn_texture_normal: Button
    btn_texture_minecraft: Button
    btn_gamemode_classic: Button
    btn_gamemode_item: Button
    btn_size_big: Button
    btn_size_medium: Button
    btn_size_small: Button
    btn_dynamite: Button
    btn_map: Button
    btn_shuffle: Button
    texture: Texture

    def __init__(self):
        self.gamemode = "classic"
        self.choosed_texture = "normal"
        self.field_height = 10
        self.field_width = 10
        self.is_btn_small = True

    def setting_window(self):
        tk.title("設定画面")
        canvas.create_text(200, 30, text="設定画面", font=('Times', 20))
        canvas.create_text(100, 70, text="ゲームモードの設定", font=('Times', 15))
        canvas.create_text(90, 250, text="テクスチャの設定", font=('Times', 15))
        canvas.create_text(300, 250, text="広さの設定", font=('Times', 15))
        self.now_gamemode_id = canvas.create_text(100, 90, font=('Times', 12),
                                                  text=f"現在:{GAMEMODE_DICT[self.gamemode]}")
        self.now_texture_id = canvas.create_text(90, 280, font=('Times', 12),
                                                 text=f"現在:{TEXTURE_DICT[self.choosed_texture]}")
        self.now_fieldsize_id = canvas.create_text(300, 280, font=('Times', 12),
                                                   text=f"現在:{FIELDSIZE_DICT[self.field_width]}")
        self.btn_texture_minecraft = tkinter.Button(text="マインクラフト", font=('Times', 15),
                                                    command=self.btn_minecraft_press)
        self.btn_texture_minecraft.place(x=10, y=350)
        self.btn_texture_normal = tkinter.Button(text="ノーマル", font=('Times', 15), command=self.btn_normal_press)
        self.btn_texture_normal.place(x=40, y=300)
        self.btn_gamemode_item = tkinter.Button(text="アイテム", font=('Times', 15),
                                                command=self.btn_item_press)
        self.btn_gamemode_item.place(x=50, y=160)
        self.btn_gamemode_classic = tkinter.Button(text="クラシック", font=('Times', 15), command=self.btn_classic_press)
        self.btn_gamemode_classic.place(x=40, y=110)
        self.btn_size_big = tkinter.Button(text="大", font=('Times', 15), command=self.btn_big_press)
        self.btn_size_big.place(x=220, y=300)
        self.btn_size_medium = tkinter.Button(text="中", font=('Times', 15), command=self.btn_medium_press)
        self.btn_size_medium.place(x=290, y=300)
        if self.gamemode != "item":
            self.btn_size_small = tkinter.Button(text="小", font=('Times', 15), command=self.btn_small_press)
            self.btn_size_small.place(x=350, y=300)
        self.btn_start = tkinter.Button(text="始める", font=('Times', 15), command=self.btn_start_press)
        self.btn_start.place(x=250, y=100)

    def set(self):
        tk.title("マインスイーパー")
        canvas.delete("all")
        self.rock = 0
        self.field = []
        self.set_field()
        self.set_bomb()
        self.on_dynamite = False
        self.on_map = False
        self.rest_dynamite = 1
        self.rest_map = 1
        self.rest_shuffle = 1
        # self.print_field()
        self.rock_text_id = canvas.create_text(160, self.field_height * 32 + 60, font=('Times', 15),
                                               text=f'ロックしたマスの数：{self.rock}/{self.number_of_bomb}')
        if self.gamemode == "item":
            canvas.create_text(self.field_width * 32 + 150, 220, text="アイテム", font=("Times", 15))
            self.rest_dynamite_id = canvas.create_text(self.field_width * 32 + 150, 305, font=('Times', 12),
                                                       text=f'残り：{self.rest_dynamite}')
            self.rest_map_id = canvas.create_text(self.field_width * 32 + 150, 388, font=('Times', 12),
                                                  text=f'残り：{self.rest_map}')
            self.rest_shuffle_id = canvas.create_text(self.field_width * 32 + 150, 470, font=('Times', 12),
                                                      text=f'残り：{self.rest_shuffle}')
        self.texture.draw_block(self.field_width * 32 + 75, 56)
        canvas.create_text(self.field_width * 32 + 150, 56, text="：閉じたマス", font=("Times", 15))
        self.texture.draw_rock(self.field_width * 32 + 75, 106)
        canvas.create_text(self.field_width * 32 + 170, 106, text="：ロックしたマス", font=("Times", 15))
        self.texture.draw_bomb(self.field_width * 32 + 75, 156)
        canvas.create_text(self.field_width * 32 + 150, 156, text="：爆弾のマス", font=("Times", 15))
        canvas.bind('<Button-1>', self.on_left_click)
        canvas.bind('<Button-3>', self.on_right_click)

    def print_field(self):
        for row in self.field:
            nest = []
            for cell in row:
                nest.append(cell.bomb)
            print(nest)

    def set_field(self):
        for i in range(self.field_height + 2):
            nest = []
            if i == 0 or i == self.field_height + 1:
                for j in range(self.field_width + 2):
                    nest.append(Cell(i, j, "none", "none"))
            else:
                for j in range(self.field_width + 2):
                    if j == 0 or j == self.field_width + 1:
                        nest.append(Cell(i, j, "none", "none"))
                    else:
                        nest.append(Cell(i, j, "closed", "safe"))
                        self.texture.draw_block(nest[j].x, nest[j].y)
            self.field.append(nest)

    def set_bomb(self):
        for_shuffle_field = []
        for nest in self.field:
            for cell in nest:
                if cell.state != "none":
                    for_shuffle_field.append(cell)
        random.shuffle(for_shuffle_field)
        self.number_of_bomb = round(self.field_width * self.field_height / 5)
        for a in range(self.number_of_bomb):
            cell = for_shuffle_field.pop()
            cell.bomb = "bomb"

    def cell_open(self, cell):
        if cell.state == 'closed':
            cell.state = 'opened'
            if cell.bomb == 'bomb':
                canvas.create_rectangle(cell.x - 16, cell.y - 16, cell.x + 16, cell.y + 16,
                                        outline='chocolate', fill='lightgreen')
                self.texture.draw_bomb(cell.x, cell.y)
                self.check_miss()
                canvas.create_text((self.field_width * 32 + 80) / 2, (self.field_height * 32 + 80) / 2,
                                   text='GAMEOVER', font=('Times', 30))
                canvas.unbind('<Button-3>')
                canvas.unbind('<Button-1>')
            elif cell.bomb == 'safe':
                self.draw_number(cell)
                if self.clear():
                    canvas.create_text((self.field_width * 32 + 80) / 2, (self.field_height * 32 + 80) / 2,
                                       text='CLEAR', font=('Times', 30))
                    canvas.unbind('<Button-3>')
                    canvas.unbind('<Button-1>')

    def draw_number(self, cell, is_zero_open=True):
        canvas.create_rectangle(cell.x - 16, cell.y - 16, cell.x + 16, cell.y + 16,
                                outline='chocolate', fill='lightgreen')
        count = 0
        for i in range(3):
            for j in range(3):
                if self.field[cell.row - 1 + i][cell.line - 1 + j].bomb == 'bomb':
                    count = count + 1
        canvas.create_text(cell.x, cell.y, text=count)
        if is_zero_open and count == 0:
            for i in range(3):
                for j in range(3):
                    self.cell_open(self.field[cell.row - 1 + i][cell.line - 1 + j])

    def cell_rock(self, cell):
        if cell.state == 'rocked':
            cell.state = 'closed'
            self.texture.draw_block(cell.x, cell.y)
            self.rock = self.rock - 1
        elif cell.state == 'closed':
            cell.state = 'rocked'
            self.texture.draw_rock(cell.x, cell.y)
            self.rock = self.rock + 1
        canvas.delete(self.rock_text_id)
        self.rock_text_id = canvas.create_text(160, self.field_height * 32 + 60, font=('Times', 15),
                                               text=f'ロックしたマスの数：{self.rock}/{self.number_of_bomb}')

    def number_open(self, cell):
        bombs = 0
        rocks = 0
        for i in range(3):
            for j in range(3):
                if self.field[cell.row - 1 + i][cell.line - 1 + j].bomb == 'bomb':
                    bombs = bombs + 1
                if self.field[cell.row - 1 + i][cell.line - 1 + j].state == 'rocked':
                    rocks = rocks + 1
        if rocks == bombs:
            for i in range(3):
                for j in range(3):
                    self.cell_open(self.field[cell.row - 1 + i][cell.line - 1 + j])

    def clear(self):
        for nest in self.field:
            for cell in nest:
                if cell.bomb == 'safe':
                    if cell.state != 'opened':
                        return False
        return True

    def check_miss(self):
        for i in range(self.field_height + 2):
            for j in range(self.field_width + 2):
                cell = self.field[i][j]
                if cell.state == 'rocked' and cell.bomb == 'safe':
                    canvas.create_line(cell.x - 16, cell.y - 16, cell.x + 16, cell.y + 16)
                    canvas.create_line(cell.x - 16, cell.y + 16, cell.x + 16, cell.y - 16)

    def map(self, cell):
        self.rest_map -= 1
        canvas.delete(self.rest_map_id)
        self.rest_map_id = canvas.create_text(self.field_width * 32 + 150, 388, font=('Times', 12),
                                              text=f'残り：{self.rest_map}')
        for i in range(5):
            for j in range(5):
                if 0 <= cell.row - 2 + i <= self.field_height + 1 and 0 <= cell.line - 2 + j <= self.field_width + 1:
                    if (self.field[cell.row - 2 + i][cell.line - 2 + j].state == "closed"
                            and self.field[cell.row - 2 + i][cell.line - 2 + j].bomb == "bomb"):
                        self.cell_rock(self.field[cell.row - 2 + i][cell.line - 2 + j])

    def ready_map(self):
        if self.on_map:
            self.on_map = False
            self.btn_map.configure(bg="white")
        elif self.rest_map != 0:
            if self.on_dynamite:
                self.ready_dynamite()
            self.on_map = True
            self.btn_map.configure(bg="orange")

    def ready_dynamite(self):
        if self.on_dynamite:
            self.on_dynamite = False
            self.btn_dynamite.configure(bg="white")
        elif self.rest_dynamite != 0:
            if self.on_map:
                self.ready_map()
            self.on_dynamite = True
            self.btn_dynamite.configure(bg="orange")

    def dynamite(self, cell):
        self.rest_dynamite -= 1
        canvas.delete(self.rest_dynamite_id)
        self.rest_dynamite_id = canvas.create_text(self.field_width * 32 + 150, 305, font=('Times', 12),
                                                   text=f'残り：{self.rest_dynamite}')
        count = 0
        for i in range(3):
            for j in range(3):
                if self.field[cell.row - 1 + i][cell.line - 1 + j].state != "none":
                    if self.field[cell.row - 1 + i][cell.line - 1 + j].bomb == "bomb":
                        count += 1
                    self.field[cell.row - 1 + i][cell.line - 1 + j].bomb = "safe"
                    self.field[cell.row - 1 + i][cell.line - 1 + j].state = "opened"
        self.number_of_bomb -= count
        canvas.delete(self.rock_text_id)
        self.rock_text_id = canvas.create_text(160, self.field_height * 32 + 60, font=('Times', 15),
                                               text=f'ロックしたマスの数：{self.rock}/{self.number_of_bomb}')
        for i in range(5):
            for j in range(5):
                if 0 <= cell.row - 2 + i <= self.field_height + 1 and 0 <= cell.line - 2 + j <= self.field_width + 1:
                    if self.field[cell.row - 2 + i][cell.line - 2 + j].state == "opened":
                        self.draw_number(self.field[cell.row - 2 + i][cell.line - 2 + j], False)

    def field_shuffle(self):
        if self.rest_shuffle != 0:
            self.rest_shuffle -= 1
            canvas.delete(self.rest_shuffle_id)
            self.rest_shuffle_id = canvas.create_text(self.field_width * 32 + 150, 470, font=('Times', 12),
                                                      text=f'残り：{self.rest_shuffle}')
            canvas.delete(self.rock_text_id)
            self.rock = 0
            self.rock_text_id = canvas.create_text(160, self.field_height * 32 + 60, font=('Times', 15),
                                                   text=f'ロックしたマスの数：0/{self.number_of_bomb}')
            bomb_count = 0
            cell_list = []
            for floor in self.field:
                for cell in floor:
                    if cell.state == "rocked":
                        cell.state = "closed"
                        self.texture.draw_block(cell.x, cell.y)
                    if cell.bomb == "bomb":
                        bomb_count += 1
                        cell.bomb = "safe"
                    if cell.state == "closed":
                        cell_list.append(cell)
            random.shuffle(cell_list)
            for a in range(bomb_count):
                cell = cell_list.pop()
                cell.bomb = "bomb"
            for floor in self.field:
                for cell in floor:
                    if cell.state == "opened":
                        self.draw_number(cell, False)

    def btn_start_press(self):
        self.btn_texture_minecraft.place_forget()
        self.btn_texture_normal.place_forget()
        self.btn_gamemode_classic.place_forget()
        self.btn_gamemode_item.place_forget()
        self.btn_size_big.place_forget()
        self.btn_size_medium.place_forget()
        self.btn_size_small.place_forget()
        self.btn_start.place_forget()
        if self.gamemode == "item":
            self.btn_dynamite = tkinter.Button(text="ダイナマイト", font=('Times', 15), command=self.ready_dynamite)
            self.btn_dynamite.place(x=self.field_width * 32 + 80, y=250)
            self.btn_map = tkinter.Button(text="地図", font=('Times', 15), command=self.ready_map)
            self.btn_map.place(x=self.field_width * 32 + 120, y=330)
            self.btn_shuffle = tkinter.Button(text="シャッフル", font=('Times', 15), command=self.field_shuffle)
            self.btn_shuffle.place(x=self.field_width * 32 + 90, y=410)
        self.btn_stop = tkinter.Button(text="やめる", font=('Times', 15), command=tk.destroy)
        self.btn_stop.place(x=(self.field_width * 32 + 250) / 2, y=self.field_height * 32 + 80)
        self.btn_back = tkinter.Button(text="設定画面に戻る", font=('Times', 15), command=self.btn_back_press)
        self.btn_back.place(x=(self.field_width * 64 + 500) / 7, y=self.field_height * 32 + 130)
        self.btn_continue = tkinter.Button(text="やり直す", font=('Times', 15), command=self.btn_continue_press)
        self.btn_continue.place(x=(self.field_width * 32 + 250) / 5, y=self.field_height * 32 + 80)
        canvas.configure(width=self.field_width * 32 + 250, height=self.field_height * 32 + 180, bg='#80C0ff')
        self.texture = Texture(canvas, self.choosed_texture)
        self.set()

    def btn_normal_press(self):
        self.choosed_texture = "normal"
        canvas.delete(self.now_texture_id)
        self.now_texture_id = canvas.create_text(90, 280, font=('Times', 12),
                                                 text=f"現在:{TEXTURE_DICT[self.choosed_texture]}")

    def btn_minecraft_press(self):
        self.choosed_texture = "minecraft"
        canvas.delete(self.now_texture_id)
        self.now_texture_id = canvas.create_text(90, 280, font=('Times', 12),
                                                 text=f"現在:{TEXTURE_DICT[self.choosed_texture]}")

    def btn_classic_press(self):
        self.gamemode = "classic"
        if not self.is_btn_small:
            self.btn_size_small = tkinter.Button(text="小", font=('Times', 15), command=self.btn_small_press)
            self.btn_size_small.place(x=350, y=300)
            self.is_btn_small = True
        canvas.delete(self.now_gamemode_id)
        self.now_gamemode_id = canvas.create_text(100, 90, font=('Times', 12),
                                                  text=f"現在:{GAMEMODE_DICT[self.gamemode]}")

    def btn_item_press(self):
        self.gamemode = "item"
        if self.is_btn_small:
            self.btn_size_small.place_forget()
            if self.field_height == 5:
                self.btn_medium_press()
            self.is_btn_small = False
        canvas.delete(self.now_gamemode_id)
        self.now_gamemode_id = canvas.create_text(100, 90, font=('Times', 12),
                                                  text=f"現在:{GAMEMODE_DICT[self.gamemode]}")

    def btn_big_press(self):
        self.field_height = 20
        self.field_width = 20
        canvas.delete(self.now_fieldsize_id)
        self.now_fieldsize_id = canvas.create_text(300, 280, font=('Times', 12),
                                                   text=f"現在:{FIELDSIZE_DICT[self.field_width]}")

    def btn_medium_press(self):
        self.field_height = 10
        self.field_width = 10
        canvas.delete(self.now_fieldsize_id)
        self.now_fieldsize_id = canvas.create_text(300, 280, font=('Times', 12),
                                                   text=f"現在:{FIELDSIZE_DICT[self.field_width]}")

    def btn_small_press(self):
        self.field_height = 5
        self.field_width = 5
        canvas.delete(self.now_fieldsize_id)
        self.now_fieldsize_id = canvas.create_text(300, 280, font=('Times', 12),
                                                   text=f"現在:{FIELDSIZE_DICT[self.field_width]}")

    def btn_continue_press(self):
        canvas.delete(self.rock_text_id)
        if self.gamemode == "item":
            canvas.delete(self.rest_dynamite_id)
            canvas.delete(self.rest_map_id)
        self.set()

    def btn_back_press(self):
        canvas.unbind('<Button-3>')
        canvas.unbind('<Button-1>')
        self.btn_continue.place_forget()
        self.btn_stop.place_forget()
        self.btn_back.place_forget()
        if self.gamemode == "item":
            self.btn_dynamite.place_forget()
            self.btn_map.place_forget()
            self.btn_shuffle.place_forget()
        canvas.delete("all")
        canvas.configure(width=400, height=400, bg="lightgreen")
        self.setting_window()

    def on_left_click(self, event):
        if (40 <= event.x <= 40 + 32 * self.field_width
                and 40 <= event.y <= 40 + 32 * self.field_height):
            x = event.x - 8
            y = event.y - 8
            x = x // 32
            y = y // 32
            if self.on_dynamite:
                self.dynamite(self.field[y][x])
                self.ready_dynamite()
            elif self.on_map:
                self.map(self.field[y][x])
                self.ready_map()
            else:
                if self.field[y][x].state == 'opened':
                    self.number_open(self.field[y][x])
                else:
                    self.cell_open(self.field[y][x])

    def on_right_click(self, event):
        x = event.x - 8
        y = event.y - 7
        x = x // 32
        y = y // 32
        self.cell_rock(self.field[y][x])


# ----------------------------------------------------------------------------------------------------------------------

tk = Tk()
canvas = Canvas(tk, width=400, height=400, bg="lightgreen")
canvas.pack()
tk.geometry("+30+30")

box = Box()
box.setting_window()
tk.mainloop()
