import random

# ==========
NUMBER_OF_SPLIT = 4  # 分割する回数


# ==========

class Room:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    # この部屋と境界線との最短距離を返す
    def wall_dist(self, muki, border):
        if muki == "tate":
            if abs(self.x0 - border) < abs(self.x1 - border):
                return abs(self.x0 - border - 1)
            else:
                return abs(self.x1 - border + 1)
        if muki == "yoko":
            if abs(self.y0 - border) < abs(self.y1 - border):
                return abs(self.y0 - border - 1)
            else:
                return abs(self.y1 - border + 1)

    # このエリアを2つに分けて返す
    def split_area(self, muki):
        if muki == "tate":
            border = random.randint(self.x0, self.x1)
            if border - self.x0 > 1 and self.x1 - border > 1:
                # self.print_room()
                # print(border)
                # Room(self.x0, self.y0, border - 1, self.y1).print_room()
                # Room(border + 1, self.y0, self.x1, self.y1).print_room()
                return [Room(self.x0, self.y0, border - 1, self.y1),
                        Room(border + 1, self.y0, self.x1, self.y1)], border
        else:
            border = random.randint(self.y0, self.y1)
            if border - self.y0 > 1 and self.y1 - border > 1:
                return [Room(self.x0, self.y0, self.x1, border - 1),
                        Room(self.x0, border + 1, self.x1, self.y1)], border
        return [Room(self.x0, self.y0, self.x1, self.y1)], border

    # このエリアの中からランダムで一個部屋を作って返す
    def make_room(self):
        x_list = list(range(self.x0, self.x1 + 1))
        x0 = random.randint(0, len(x_list) - 1)
        x0 = x_list.pop(x0)
        x1 = random.randint(0, len(x_list) - 1)
        x1 = x_list.pop(x1)
        if x0 > x1:
            x0, x1 = x1, x0
        y_list = list(range(self.y0, self.y1 + 1))
        y0 = random.randint(0, len(y_list) - 1)
        y0 = y_list.pop(y0)
        y1 = random.randint(0, len(y_list) - 1)
        y1 = y_list.pop(y1)
        if y0 > y1:
            y0, y1 = y1, y0
        # self.print_room()
        # print([x0, y0, x1, y1])
        # print()
        return Room(x0, y0, x1, y1)

    # この部屋の座標を表示
    def print_room(self):
        print([self.x0, self.y0, self.x1, self.y1])


class Map:
    floor_map: list
    rooms: list
    width: int
    height: int

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.floor_map = []

    def init_map(self):
        # マップを1で埋める
        self.floor_map = []
        for y in range(self.height):
            lis = []
            for x in range(self.width):
                lis.append(1)
            self.floor_map.append(lis)

        # 大本となるエリア
        # 一回り内側のエリアにすることで少なくとも一番外側に壁ができるようにしている
        area = Room(1, 1, self.width - 2, self.height - 2)
        # area.draw()

        # 部屋分け
        self.rooms = self.make_map(area, NUMBER_OF_SPLIT)

        # 部屋にあたるセルの座標を全部持っておいてその中からランダムに取り出して
        # 初期位置に設定する形にしている
        # こうするとアイテムなど同士の重なりが防げる
        init_places = []

        # 各部屋に対応するマップ上のセルに0を入れる
        for room in self.rooms:
            # room.draw("white")
            for y in range(room.y0, room.y1 + 1):
                for x in range(room.x0, room.x1 + 1):
                    self.floor_map[y][x] = 0
                    init_places.append([x, y])

        random.shuffle(init_places)

        # アイテム配置
        if random.random() < 0.25:
            item_num = 3
        elif random.random() < 0.5:
            item_num = 5
        else:
            item_num = 4
        for a in range(item_num):
            place = init_places.pop()
            self.floor_map[place[1]][place[0]] = 2

        # 階段配置
        place = init_places.pop()
        self.floor_map[place[1]][place[0]] = 3
        # self.print_map()

        return init_places

    def make_map(self, room, depth):
        if depth > 0:
            muki = random.choice(["tate", "yoko"])  # 縦に割るか横に割るか

            # エリアを分割(しようとする)
            areas, border = room.split_area(muki)
            if len(areas) == 2:  # 分割に成功したら
                # 分割した部屋それぞれをさらに分割
                # 孫とかも含めて子以下の部屋が全てリストになったものが返ってくる
                rooms1 = self.make_map(areas[0], depth - 1)
                rooms2 = self.make_map(areas[1], depth - 1)

                # 分割した境界線と一番近い部屋を選出
                room1 = nearest_room_in(rooms1, muki, border)
                room2 = nearest_room_in(rooms2, muki, border)

                # 選んだ2つの部屋の間に通路を引く
                self.make_path(room1, room2, muki, border)
                rooms = rooms1 + rooms2
            else:
                rooms = self.make_map(areas[0], depth - 1)
            return rooms
        else:
            # self.draw()
            return [room.make_room()]

    # 部屋2つを受け取ってその間に通路を引く
    def make_path(self, room1, room2, muki, border):
        if muki == "tate":
            y1 = random.randint(room1.y0, room1.y1)
            y2 = random.randint(room2.y0, room2.y1)
            for i in range(room1.x1 + 1, border):
                self.floor_map[y1][i] = 0
            for i in range(room2.x0 - 1, border, -1):
                self.floor_map[y2][i] = 0
            if y1 > y2:
                y1, y2 = y2, y1
            for i in range(y1, y2 + 1):
                self.floor_map[i][border] = 0
        if muki == "yoko":
            x1 = random.randint(room1.x0, room1.x1)
            x2 = random.randint(room2.x0, room2.x1)
            for i in range(room1.y1 + 1, border):
                self.floor_map[i][x1] = 0
            for i in range(room2.y0 - 1, border, -1):
                self.floor_map[i][x2] = 0
            if x1 > x2:
                x1, x2 = x2, x1
            for i in range(x1, x2 + 1):
                self.floor_map[border][i] = 0

    # デバッグ用、マップをコンソールに表示する
    def print_map(self):
        for line in self.floor_map:
            print(line)

    def get_map(self):
        return self.floor_map

    # 全部屋の中の何もないセルの座標をリストにまとめて返す
    def room_pos_list(self, origin_x, origin_y):
        pos_list = []
        for room in self.rooms:
            if room.x0 <= origin_x <= room.x1 and room.y0 <= origin_y <= room.y1:
                continue  # 元々いた部屋とは違う部屋を選ぶ
            for y in range(room.y0, room.y1 + 1):
                for x in range(room.x0, room.x1 + 1):
                    if self.floor_map[y][x] == 0:
                        pos_list.append([x, y])
        random.shuffle(pos_list)
        return pos_list


# 受け取った部屋群の中から境界線に最も近い部屋を返す
def nearest_room_in(rooms, muki, border):
    nearest_room = rooms[0]
    distance = nearest_room.wall_dist(muki, border)
    for room in rooms:
        dist = room.wall_dist(muki, border)
        if distance > dist:
            distance = dist
            nearest_room = room
    return nearest_room
