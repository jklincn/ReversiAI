import ctypes
import sys
import random
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext
from enum import Enum


# 输出重定向到窗口中
class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, str):
        self.text_space.insert("end", str)
        self.text_space.update()
        self.text_space.yview_moveto(1.0)

    def flush(self):
        pass


# 棋手
class Player(Enum):
    HUMAN = 0
    AI = 1


# 棋子类型
class ChessPiece(Enum):
    DEFAULT = 0
    WHITE = 1
    BLACK = 2


# 下棋状态
class GameState(Enum):
    NotStart = 0
    WAIT_WHITE = 1
    WAIT_BLACK = 2
    FINISH = 3


class Position:
    def __init__(self, col=-1, row=-1):
        self.col = col
        self.row = row


# 控制棋局状态
class ReversiData:
    def __init__(self):

        # 当前棋盘数据,先列后行
        #  0 -------------> x
        #  |
        #  |
        #  |
        #  |
        #  y

        self.board = [[ChessPiece.DEFAULT] * 8 for _ in range(8)]
        self.board[3][3] = ChessPiece.WHITE
        self.board[3][4] = ChessPiece.BLACK
        self.board[4][3] = ChessPiece.BLACK
        self.board[4][4] = ChessPiece.WHITE

        self.state = GameState.WAIT_BLACK
        self.first = random.choice(list(Player))

        self.white_chesspiece = [Position(3,3),Position(4,4)]
        self.black_chesspiece = [Position(3,4),Position(4,3)]


# 控制图形化界面
class ReversiGUI(tk.Tk):
    board: tk.Canvas
    info: scrolledtext.ScrolledText

    def __init__(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 设置高分辨率自适应
        super().__init__()
        self.title("Reversi AI")

        # 窗口大小位置自适应
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = screen_width // 5 * 3  # 预设成屏幕宽度的3/5
        if screen_width / screen_height == 16 / 9:
            width = screen_width // 2  # 细微优化：16:9 的屏幕设为屏幕宽度的1/2会更好看
        height = screen_height // 2  # 预设成屏幕高度的1/2
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(width=False, height=False)

        # 设置棋盘
        # fmt: off
        # 格子宽度设为一半再向 8 取整
        self.line_width = (height-10) // 8
        self.board = tk.Canvas(self, width=self.line_width*8, height=self.line_width*8, borderwidth=2, relief="ridge", bg="#FCD57D")
        self.board.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        # 绑定鼠标事件
        self.board.bind("<Button-1>", click_left)
        self.board.bind("<Button-3>", click_right)

        # 设置算法信息输出窗口
        self.info = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.NORMAL, font=("微软雅黑", 12))
        self.info.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        sys.stdout = StdoutRedirector(self.info)
        # fmt: on
        # 输出一些初始化信息
        print("Reversi AI - 使用 MCTS 算法实现黑白棋 Al 棋手")
        print("小组成员: 林杰克、邹国强、吴逸群、徐俊州")
        print("使用鼠标左键下棋，使用鼠标右键可以重置棋局")
        print("-------------------------------------------------------")
        who_first()

        # 画棋盘
        self.draw()

    def draw(self):
        # 清除画布
        self.board.delete("all")
        # 画线
        # fmt: off
        for i in range(8):
            self.board.create_line(0, i * self.line_width, self.line_width * 8, i * self.line_width, fill="black")
            self.board.create_line(i * self.line_width, 0, i * self.line_width, self.line_width * 8, fill="black")
        # fmt: on
        # 画棋子
        for col in range(8):
            for row in range(8):
                # 5 点偏移量是为了美观性
                if data.board[col][row] == ChessPiece.WHITE:
                    self.board.create_oval(
                        self.line_width * col + 5,
                        self.line_width * row + 5,
                        self.line_width * (col + 1) - 5,
                        self.line_width * (row + 1) - 5,
                        fill="white",
                        width=2,
                    )
                elif data.board[col][row] == ChessPiece.BLACK:
                    self.board.create_oval(
                        self.line_width * col + 5,
                        self.line_width * row + 5,
                        self.line_width * (col + 1) - 5,
                        self.line_width * (row + 1) - 5,
                        fill="black",
                        width=2,
                    )


def click_left(event):
    global data
    col = event.x // gui.line_width
    row = event.y // gui.line_width
    # 由于画布的边缘距离所以特殊处理，画布有边缘更美观
    if col == 8:
        col = col - 1
    pos = Position(col, row)
    print(col, row)

    # todo

    if data.state == GameState.WAIT_BLACK:
        data.board[col][row] = ChessPiece.BLACK
        data.state = GameState.WAIT_WHITE
    elif data.state == GameState.WAIT_WHITE:
        data.board[col][row] = ChessPiece.WHITE
        data.state = GameState.WAIT_BLACK
    gui.draw()


def candidate_position():
    pos = []
    if data.state == GameState.WAIT_BLACK:
        # todo
        pass
    elif data.state == GameState.WAIT_WHITE:
        # todo
        pass


def click_right(event):
    global data
    data = ReversiData()
    print("棋局已重置")
    gui.draw()
    who_first()


def who_first():
    if data.first == Player.HUMAN:
        print("对局开始，你持黑棋")
    else:
        print("对局开始，你持白棋")


if __name__ == "__main__":
    global data, gui

    data = ReversiData()

    gui = ReversiGUI()

    gui.mainloop()
