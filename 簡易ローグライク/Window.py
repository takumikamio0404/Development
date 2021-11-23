class Window:
    def __init__(self, canvas):
        self.canvas = canvas
        self.choosed_cell_num = 0
        self.choosed_choice = 0
        self.items = []

    def get_canvas(self):
        return self.canvas

    # ゲームオーバー画面
    def game_over(self, cause, floor, last_level, steps, defeat, damage, item):
        self.canvas.create_rectangle([50, 100, 450, 400], fill="white")
        self.canvas.create_text(250, 150, text="GAME OVER", font=('Times', 25))
        if cause == "attack":
            self.canvas.create_text(250, 195, text="Playerは敵の攻撃によって力尽きた", font=('Times', 14))
        elif cause == "hunger":
            self.canvas.create_text(250, 195, text="Playerは飢えて力尽きた", font=('Times', 15))
        self.canvas.create_text(145, 270, text=f"到達階数：{floor}\n到達レベル：{last_level}\n移動した歩数：{steps}", font=('Times', 13))
        self.canvas.create_text(330, 270, text=f"倒した敵の数：{defeat}\n受けたダメージ：{damage}\n拾ったアイテムの数：{item}", font=('Times', 13))
        self.canvas.create_text(250, 360, text="エンターキーでタイトルに戻る\n　Escキーでゲームをやめる", font=('Times', 15))

    # 階段降りるかの確認画面
    def floor_down_choice(self):
        self.canvas.create_rectangle([50, 100, 450, 400], fill="white")
        self.canvas.create_text(250, 200, text="階段がある", font=('Times', 20))
        self.canvas.create_text(250, 280, text="降りますか？", font=('Times', 15))
        self.canvas.create_text(200, 330, text="降りる", font=('Times', 13))
        self.canvas.create_text(300, 330, text="降りない", font=('Times', 13))
        if self.choosed_choice == 0:
            self.canvas.create_polygon([157, 323, 170, 330, 157, 337])
        elif self.choosed_choice == 1:
            self.canvas.create_polygon([247, 323, 260, 330, 247, 337])

    def change_choice(self):
        if self.choosed_choice == 0:
            self.choosed_choice = 1
        elif self.choosed_choice == 1:
            self.choosed_choice = 0

    def is_floor_down(self):
        if self.choosed_choice == 0:
            self.choosed_cell_num = 0
            return True
        else:
            self.choosed_choice = 0
            return False

    # インベントリ画面
    def inventory(self, player, floor):
        self.items = player.items
        if player.satiety <= 0:
            color = "red"
        else:
            color = "black"
        self.canvas.create_rectangle([50, 100, 450, 400], fill="white")
        self.canvas.create_text(50, 100, anchor="nw", text="Player", font=('Times', 24))
        self.canvas.create_text(450, 100, anchor="ne", text=f"{floor}階", font=('Times', 24))
        self.canvas.create_text(50, 140, anchor="nw", text=f"HP: {player.hp}/{player.maxhp}", font=('Times', 18))
        self.canvas.create_rectangle([55, 170, 350, 190], fill="white")
        self.canvas.create_rectangle([55, 170, 300 * player.hp / player.maxhp + 55, 190], fill="blue")
        self.canvas.create_text(50, 210, anchor="nw", text=f"空腹度: {player.satiety}/100", font=('Times', 18), fill=color)
        self.canvas.create_rectangle([55, 240, 350, 260], fill="white")
        self.canvas.create_rectangle([55, 240, 300 * player.satiety / 100 + 55, 260], fill="blue")
        self.canvas.create_text(50, 280, anchor="nw", text=f"Lv.{player.level}", font=('Times', 20))
        self.canvas.create_text(50, 310, anchor="nw", text=f"経験値: {player.total_exp}", font=('Times', 16))
        self.canvas.create_text(50, 330, anchor="nw",
                                text=f"次のレベルまで: {round(10 * 1.1 ** (player.level - 1)) - player.exp}",
                                font=('Times', 16))
        for i in range(10):
            if i == self.choosed_cell_num:
                self.canvas.create_rectangle(50 + 40 * i, 360, 50 + 40 * (i + 1), 400, fill="skyblue")
            self.canvas.create_rectangle(50 + 40 * i, 360, 50 + 40 * (i + 1), 400)
            if len(player.items) > i:
                if player.items[i][0] == "heal":
                    self.draw_heal(50 + 40 * i, 360)
                elif player.items[i][0] == "arrow":
                    self.draw_arrow(50 + 40 * i, 360, player.items[i][1])
                elif player.items[i][0] == "food":
                    self.draw_food(50 + 40 * i, 360)
                elif player.items[i][0] == "wand":
                    self.draw_wand(50 + 40 * i, 360)

    def draw_heal(self, x, y):
        self.canvas.create_rectangle([x + 9, y + 15, x + 31, y + 35], width=0, fill="pink")
        self.canvas.create_rectangle([x + 12, y + 4, x + 28, y + 10], width=0, fill="darkgoldenrod")
        self.canvas.create_rectangle([x + 9, y + 7, x + 31, y + 35])

    def draw_arrow(self, x, y, stock):
        self.canvas.create_line([x + 35, y + 35, x + 5, y + 5], arrow="last", width=4)
        self.canvas.create_text(x + 40, y, anchor="ne", text=f"{stock}", font=('Times', 16))

    def draw_food(self, x, y):
        self.canvas.create_polygon([x + 3, y + 35, x + 20, y + 5, x + 37, y + 35], outline="black", fill="white")
        self.canvas.create_rectangle([x + 14, y + 23, x + 26, y + 35], fill="black")

    def draw_wand(self, x, y):
        self.canvas.create_line([x + 35, y + 35, x + 10, y + 10], width=4, fill="darkgoldenrod")
        self.canvas.create_oval([x + 5, y + 5, x + 15, y + 15], width=0, fill="lightcoral")
        self.canvas.create_line([x + 10, y + 18, x + 18, y + 10], width=3, fill="orange")

    def move_cursor(self, muki):
        if muki == "right":
            self.choosed_cell_num += 1
            if self.choosed_cell_num == 10:
                self.choosed_cell_num = 0
        elif muki == "left":
            self.choosed_cell_num -= 1
            if self.choosed_cell_num == -1:
                self.choosed_cell_num = 9

    def choose_item(self):
        if len(self.items) > self.choosed_cell_num:
            if self.items[self.choosed_cell_num][0] == "arrow":
                self.items[self.choosed_cell_num][1] -= 1
                if self.items[self.choosed_cell_num][1] == 0:
                    return self.items.pop(self.choosed_cell_num)[0]
                else:
                    return self.items[self.choosed_cell_num][0]
            else:
                return self.items.pop(self.choosed_cell_num)[0]
        else:
            return ""
