"""
穴掘り法での迷路生成
"""
import random


class Maze:
    maze: list
    mark: list
    width: int
    height: int

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.set_field()
        self.set_mark()
        random.shuffle(self.mark)
        self.process = self.mark[0]  # 初期処理位置をmarkの中からランダムにひとつ取り出す
        self.process.state = "path"  # 初期処理位置を道にする
        while True:
            # 処理位置の上下左右2マス先のうち壁のマスを記録しておき、その中からランダムで一つ選び、その2マスを道にする
            checks = []
            for a in range(2):
                for b in range(2):
                    height = self.process.height + 2 * a * (1 - 2 * b)  # (a,b)が(0,0)→0,(0,1)→0,(1,0)→2,(1,1)→-2
                    width = self.process.width + 2 * (1 - a) * (1 - 2 * b)  # (a,b)が(0,0)→2,(0,1)→-2,(1,0)→0,(1,1)→0
                    check = self.maze[height][width]
                    if check.state == "wall":
                        checks.append(check)
            if len(checks) != 0:  # 周りに壁のマスがあれば
                cell = random.choice(checks)  # 移動先のマス
                between_cell_height = round((cell.height + self.process.height) / 2)  # 間のマス
                between_cell_width = round((cell.width + self.process.width) / 2)
                between_cell = self.maze[between_cell_height][between_cell_width]
                between_cell.state = "path"
                self.process = cell  # 処理位置を移動先のマスにする
                self.process.state = "path"  # 処理位置を道にする
            else:  # 周りに壁がなければ(行き止まりなら)
                self.process.stop = True  # 処理位置を行き止まりにする
                check = 0
                for cell in self.mark:
                    if cell.state == "path" and not cell.stop:  # 行き止まりでない道のうち一つを処理位置にして繰り返す
                        self.process = cell
                        check = 1
                        break
                if check == 0:  # mark全部が行き止まりになったらループを抜ける
                    break
        self.convert()

    def set_mark(self):
        # 偶数行偶数列のマスをまとめておく
        self.mark = []
        for height in self.maze:
            for cell in height:
                if cell.state == "wall" and cell.height % 2 == 0 and cell.width % 2 == 0:
                    self.mark.append(cell)

    def set_field(self):
        # 縦横指定サイズより一回り大きい範囲を回して一番外側の状態をnoneにする
        # 要するに盤面の外側に状態がnoneの膜を作る
        self.maze = []  # mazeを初期化
        for height in range(self.height + 2):
            nest = []  # nestを初期化
            for width in range(self.width + 2):
                if height == 0 or height == self.height + 1:
                    nest.append(Cell(height, width, "none"))
                elif width == 0 or width == self.width + 1:
                    nest.append(Cell(height, width, "none"))
                else:
                    nest.append(Cell(height, width))
            self.maze.append(nest)

    def convert(self):  # mazeを文字型から数字型にする
        converted_maze = []
        for path in self.maze:
            nest = []
            for cell in path:
                if cell.state == "wall":  # ここでnoneが消える
                    nest.append(0)
                elif cell.state == "path":
                    nest.append(1)
            if len(nest) != 0:
                converted_maze.append(nest)
        self.maze = converted_maze


class Cell:
    height: int
    width: int
    state: str
    stop: bool

    def __init__(self, height, width, state="wall", stop=False):
        self.height = height
        self.width = width
        self.state = state
        self.stop = stop
