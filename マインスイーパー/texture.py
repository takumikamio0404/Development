from dataclasses import dataclass


@dataclass
class Texture:
    def __init__(self, canvas, texture):
        self.canvas = canvas
        self.texture = texture

    def draw_block(self, x, y):
        if self.texture == "minecraft":
            self.grass(x, y)
        else:
            self.block(x, y)

    def draw_rock(self, x, y):
        if self.texture == "minecraft":
            self.TNT(x, y)
        else:
            self.frag(x, y)

    def draw_bomb(self, x, y):
        if self.texture == "minecraft":
            self.creeper(x, y)
        else:
            self.bomb(x, y)

    def block(self, x, y):
        self.canvas.create_rectangle(x - 16, y - 16,
                                     x + 16, y + 16,
                                     outline='sienna', fill="#44aa44")

    def frag(self, x, y):
        self.canvas.create_polygon(x - 5, y - 10,
                                   x - 5, y,
                                   x + 5, y - 5, fill="red", outline="red")
        self.canvas.create_line(x - 5, y - 10,
                                x - 5, y + 10)

    def bomb(self, x, y):
        self.canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="black")
        self.canvas.create_line(x + 8, y - 8, x - 8, y + 8, width=2)
        self.canvas.create_line(x - 8, y - 8, x + 8, y + 8, width=2)
        self.canvas.create_line(x - 12, y, x + 12, y, width=2)
        self.canvas.create_line(x, y - 12, x, y + 12, width=2)
        self.canvas.create_oval(x - 3, y - 3, x - 1, y - 1, fill="white", outline="white")

    def creeper(self, x, y):
        self.canvas.create_rectangle(x - 16, y - 16, x + 16, y + 16, fill='#00ff00', outline='chocolate')
        self.canvas.create_rectangle(x - 12, y - 10, x - 4, y - 2, fill='black')
        self.canvas.create_rectangle(x + 4, y - 10, x + 12, y - 2, fill='black')
        self.canvas.create_rectangle(x - 4, y - 2, x + 4, y + 8, fill='black')
        self.canvas.create_rectangle(x - 8, y + 4, x - 4, y + 12, fill='black')
        self.canvas.create_rectangle(x + 4, y + 4, x + 8, y + 12, fill='black')

    def grass(self, x, y):
        self.canvas.create_rectangle(x - 16, y - 16, x + 16, y + 16, outline='chocolate', fill='chocolate')
        self.canvas.create_polygon(x - 16, y - 16,
                                   x - 16, y - 10,
                                   x - 14, y - 10,
                                   x - 14, y - 12,
                                   x - 12, y - 12,
                                   x - 12, y - 10,
                                   x - 8, y - 10,
                                   x - 8, y - 8,
                                   x - 6, y - 8,
                                   x - 6, y - 14,
                                   x - 4, y - 14,
                                   x - 4, y - 10,
                                   x - 2, y - 10,
                                   x - 2, y - 12,
                                   x, y - 12,
                                   x, y - 8,
                                   x + 2, y - 8,
                                   x + 2, y - 10,
                                   x + 4, y - 10,
                                   x + 4, y - 8,
                                   x + 6, y - 8,
                                   x + 6, y - 10,
                                   x + 8, y - 10,
                                   x + 8, y - 12,
                                   x + 10, y - 12,
                                   x + 10, y - 10,
                                   x + 14, y - 10,
                                   x + 14, y - 12,
                                   x + 16, y - 12,
                                   x + 16, y - 16,
                                   x - 16, y - 16,
                                   outline='#00ff00',
                                   fill='#00ff00')
        self.canvas.create_rectangle(x - 16, y - 16, x + 16, y + 16, outline='sienna')

    def TNT(self, x, y):
        self.canvas.create_rectangle(x - 16, y - 16, x + 16, y + 16, outline='chocolate', fill='red')
        self.canvas.create_rectangle(x - 15, y - 6, x + 15, y + 6, outline='white', fill='white')
        self.canvas.create_polygon(x - 12, y - 4,
                                   x - 6, y - 4,
                                   x - 6, y - 2,
                                   x - 8, y - 2,
                                   x - 8, y + 4,
                                   x - 10, y + 4,
                                   x - 10, y - 2,
                                   x - 12, y - 2,
                                   x - 12, y - 4,
                                   fill='black')
        self.canvas.create_polygon(x - 4, y - 4,
                                   x - 2, y - 4,
                                   x - 2, y - 2,
                                   x, y - 2,
                                   x, y,
                                   x + 2, y,
                                   x + 2, y - 4,
                                   x + 4, y - 4,
                                   x + 4, y + 4,
                                   x + 2, y + 4,
                                   x + 2, y + 2,
                                   x, y + 2,
                                   x, y,
                                   x - 2, y,
                                   x - 2, y + 4,
                                   x - 4, y + 4,
                                   x - 4, y - 4,
                                   fill='black')
        self.canvas.create_polygon(x + 4, y - 4,
                                   x + 12, y - 4,
                                   x + 12, y - 2,
                                   x + 10, y - 2,
                                   x + 10, y + 4,
                                   x + 8, y + 4,
                                   x + 8, y - 2,
                                   x + 6, y - 2,
                                   x + 6, y - 4,
                                   fill='black')
