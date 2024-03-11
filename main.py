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


# 棋格类型
class ChessPiece(Enum):
    DEFAULT = 0  # 空
    WHITE = 1  # 黑棋
    BLACK = 2  # 白棋


# 下棋状态
class GameState(Enum):
    NotStart = 0
    WAIT_WHITE = 1
    WAIT_BLACK = 2
    FINISH = 3


class Position:
    def __init__(self, row=-1, col=-1):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        return False

    def __hash__(self):
        return hash((self.row, self.col))
    
    def __str__(self):
        return f"[{self.row}, {self.col}]"
    
    def __repr__(self):
        return f"[{self.row}, {self.col}]"        


# 控制棋局状态
class ReversiData:
    def __init__(self):

        # 当前棋盘数据,先行后列，但画布如下图所示
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
        self.board[2][4] = ChessPiece.WHITE

        self.state = GameState.WAIT_BLACK
        self.first = random.choice(list(Player))

        self.white_chesspiece = [Position(3, 3), Position(4, 4)]
        self.black_chesspiece = [Position(3, 4), Position(4, 3)]

    def __repr__(self):
        tmp_str = "============================\n"
        tmp_str = tmp_str + f"当前状态: {self.state.name}\n"
        tmp_str = tmp_str + "0:空 1:黑棋 2:白棋 3:当前提示\n"
        # board
        for row in range(8):
            for col in range(8):
                  tmp_str = tmp_str + str(data.board[row][col].value) + " "
            tmp_str = tmp_str + "\n"
        return tmp_str


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
        self.board.bind("<Button-2>", click_debug)
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
        global data
        # 清除画布
        self.board.delete("all")
        # 画线
        # fmt: off
        for i in range(8):
            self.board.create_line(0, i * self.line_width, self.line_width * 8, i * self.line_width, fill="black")
            self.board.create_line(i * self.line_width, 0, i * self.line_width, self.line_width * 8, fill="black")
        # fmt: on

        # 画棋子
        for row in range(8):
            for col in range(8):
                # 5 点偏移量是为了美观性
                if data.board[row][col] == ChessPiece.WHITE:
                    self.board.create_oval(
                        self.line_width * col + 5,
                        self.line_width * row + 5,
                        self.line_width * (col + 1) - 5,
                        self.line_width * (row + 1) - 5,
                        fill="white",
                        width=2,
                    )
                elif data.board[row][col] == ChessPiece.BLACK:
                    self.board.create_oval(
                        self.line_width * col + 5,
                        self.line_width * row + 5,
                        self.line_width * (col + 1) - 5,
                        self.line_width * (row + 1) - 5,
                        fill="black",
                        width=2,
                    )
        
        # 画暗示位置
        for _, pos in enumerate(candidate_position()):
            self.board.create_oval(
                        self.line_width * pos.row + 5,
                        self.line_width * pos.col + 5,
                        self.line_width * (pos.row + 1) - 5,
                        self.line_width * (pos.col + 1) - 5,
                        fill="#C1ECFF",
                        outline="#F00606",
                        dash=(5, 5),
                        width=5,
                    )


def click_left(event):
    global data
    row = event.y // gui.line_width
    col = event.x // gui.line_width
    # 由于画布的边缘距离所以特殊处理，画布有边缘更美观
    if col == 8:
        col = col - 1
    # debug code
    print("\n点击位置: ", row, col)
    t_pos_list = candidate_position()
    print("当前可落子区域: ", t_pos_list)

    if Position(row, col) in t_pos_list:
        print("确认落子: ", row, col)
        if data.state == GameState.WAIT_BLACK:
            data.board[row][col] = ChessPiece.BLACK
            data.state = GameState.WAIT_WHITE
        elif data.state == GameState.WAIT_WHITE:
            data.board[row][col] = ChessPiece.WHITE
            data.state = GameState.WAIT_BLACK
        gui.draw()


def candidate_position():
    pos = []
    if data.state == GameState.WAIT_BLACK:
        # todo
        # 遍历data.board找到可下黑棋的位置
        for row in range(8):
            for col in range(8):
                # 根据下棋规则进行判断
                if data.board[row][col] == ChessPiece.DEFAULT:
                    if is_valid_move(row, col, ChessPiece.BLACK):
                        pos.append(Position(row, col))
    elif data.state == GameState.WAIT_WHITE:
        # todo
        # 遍历data.board找到可下白棋的位置
        for row in range(8):
            for col in range(8):
                # 根据下棋规则判断位置是非可下
                if data.board[row][col] == ChessPiece.DEFAULT:
                    if is_valid_move(row, col, ChessPiece.WHITE):
                        pos.append(Position(row, col))
    return pos


def is_valid_move(row, col, rowor):
    # 依据游戏规则进行判断，该位置（row , col）可以下棋返回true
    # rowor: 本次下棋的棋子颜色
    # 该位置必须能翻转棋子才能下棋
    # 翻转规则：当自己放下的棋子在横向，竖向，斜向八个方向内有一个自己的棋子，则被夹在中间的的棋子全部翻转为自己的棋子，被夹在中间的必须是对方的棋子，不能含有空格

    # 判断该位置是否为空
    if data.board[row][col] != ChessPiece.DEFAULT:
        return False

    # 定义八个方向的偏移量，用于在棋盘上沿着这些方向进行检查
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    # 遍历八个方向
    for direction in directions:
        dx, dy = direction
        x, y = row + dx, col + dy
        flipped = False  # 是否找到可以翻转的对方棋子

        # 在当前方向上查找对方的棋子
        while 0 <= x < 8 and 0 <= y < 8:
            if data.board[x][y] == ChessPiece.DEFAULT:
                break  # 遇到空格，结束查找
            elif data.board[x][y] == rowor:
                print(f"当前判断位置({row},{col})")
                print(f"搜索位置 {x},{y}")
                if flipped:
                    return True  # 找到对方棋子且夹在中间，可以翻转
                else:
                    break  # 没有夹在中间的对方棋子，不可翻转
            else:
                flipped = True  # 发现对方棋子，标记为可翻转
            x += dx
            y += dy

    return False  # 无法在任何方向上找到可以翻转的对方棋子


def click_right(event):
    global data
    data = ReversiData()
    print("棋局已重置")
    gui.draw()
    who_first()

def click_debug(event):
    print(data)
    

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
