import ctypes
import sys
import random
import platform
import time
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from enum import Enum
import MCTS_Algorithm as rvs


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
    WHITE = 1  # 白棋
    BLACK = 2  # 黑棋


# 下棋状态
class GameState(Enum):
    # AI永远执白棋
    START = 0
    FINISH = 1


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

        self.state = GameState.START
        self.first = random.choice(list(Player))
        self.current_chesspiece_num = 4  # 当前棋子数量

    def __repr__(self):
        tmp_str = "========== 调试信息 ==========\n"
        tmp_str = tmp_str + f"当前状态: {self.state.name}\n"
        tmp_str = tmp_str + "0:空 1:白棋 2:黑棋\n"
        # board
        for row in range(8):
            for col in range(8):
                tmp_str = tmp_str + str(data.board[row][col].value) + "  "
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
        print("使用鼠标左键下棋，使用鼠标右键可以重置棋局")
        print("-------------------------------------------------------")

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
        # 判断当前棋局是否结束
        if data.state == GameState.FINISH:
            white_num = 0
            black_num = 0
            for row in range(8):
                for col in range(8):
                    if data.board[row][col] == ChessPiece.WHITE:
                        white_num = white_num + 1
                    elif data.board[row][col] == ChessPiece.BLACK:
                        black_num = black_num + 1
            who_win = lambda a, b: (
                "白棋赢" if a > b else ("黑棋赢" if b > a else "平局")
            )
            messagebox.showinfo(
                "游戏结束",
                "白棋:{}, 黑棋:{}, {}\nAI总耗时: {:.6} 秒".format(
                    white_num, black_num, who_win(white_num, black_num), total_Time
                ),
            )
            return
        else:
            # 计算黑棋可以下的地方
            t = candidate_position()
            # 判断是否有位置可下
            if not t:
                print("黑棋当前无子可下，白棋再下一回合")
                # 判断AI是否有子可下
                if not ai():
                    data.state = GameState.FINISH
                    print("双方都无子可下，提前结束棋局")
                    self.draw()
            else:
                for _, pos in enumerate(t):
                    self.board.create_oval(
                        self.line_width * pos.col + 5,
                        self.line_width * pos.row + 5,
                        self.line_width * (pos.col + 1) - 5,
                        self.line_width * (pos.row + 1) - 5,
                        fill="#C1ECFF",
                        outline="#F00606",
                        dash=(5, 5),
                        width=5,
                    )


def click_left(event):

    # todo: 避免AI还没下完的时候人类又点击鼠标

    global data
    if data.state == GameState.FINISH:
        return
    # 读取鼠标坐标，注意画布布局方向
    row = event.y // gui.line_width
    col = event.x // gui.line_width
    # 由于画布有边缘距离所以值会超一点，这里做特殊处理（画布有边缘更美观）
    if row == 8:
        row = row - 1
    if col == 8:
        col = col - 1

    # 获取当前人类可以下的棋子位置
    t = candidate_position()

    if Position(row, col) in t:
        data.board[row][col] = ChessPiece.BLACK
        # 调用 reverse() 翻转
        reverse(row, col, data.board[row][col])
        # 整个棋盘多一颗棋子
        data.current_chesspiece_num = data.current_chesspiece_num + 1
        # 判断棋局是否结束
        if data.current_chesspiece_num == 64:
            data.state = GameState.FINISH
        gui.draw()
        ai()


def transform_board():
    board = {}
    for row in range(8):
        board[row] = {}
        for col in range(8):
            board[row][col] = data.board[row][col].value
    return board


def ai():
    global total_Time
    if data.state == GameState.FINISH:
        return True
    tmp_borad = transform_board()
    # 判断AI是否无子可下
    if not rvs.possible_positions(tmp_borad, rvs.COMPUTER_NUM):
        print("白棋当前无子可下，黑棋再下一回合")
        return False
    start_time = time.perf_counter()
    row, col = rvs.mctsNextPosition(tmp_borad)
    end_time = time.perf_counter()
    total_Time = total_Time + end_time - start_time
    print(
        "白棋落子 [{}, {}], 此步耗时: {:.6} 秒".format(row, col, end_time - start_time)
    )
    data.board[row][col] = ChessPiece.WHITE
    reverse(row, col, data.board[row][col])
    data.current_chesspiece_num = data.current_chesspiece_num + 1
    if data.current_chesspiece_num == 64:
        data.state = GameState.FINISH
    gui.draw()
    return True


def reverse(row, col, color):
    # 棋局状态存储在data.board[row][col]中，当落点为(row,col)且颜色为color时，翻转需要翻转的对手棋子
    # 找到要翻转的对手棋子后将data.board[row][col]修改为另一种颜色即可，例如将黑色棋子改为白色：data.board[row][col] = ChessPiece.WHITE

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    # 遍历
    for direction in directions:
        dx, dy = direction
        x, y = row + dx, col + dy
        flipped = False  # 是否找到可以翻转的对手棋子

        # 在当前方向上查找对手的棋子
        while 0 <= x < 8 and 0 <= y < 8:
            if data.board[x][y] == ChessPiece.DEFAULT:
                break
            elif data.board[x][y] == color:
                if flipped:
                    x, y = row + dx, col + dy  # 从头翻转
                    while data.board[x][y] != color:
                        data.board[x][y] = color
                        x += dx
                        y += dy
                    break
                else:
                    break
            else:
                flipped = True  # 发现对手棋子，标记为可翻转
            x += dx
            y += dy


# 返回黑棋可能下的位置
def candidate_position():
    pos = []
    for row in range(8):
        for col in range(8):
            # 根据下棋规则判断位置是否可下
            if data.board[row][col] == ChessPiece.DEFAULT:
                if is_valid_move(row, col, ChessPiece.BLACK):
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
    print("=============================")
    gui.draw()


def click_debug(event):
    print(data)


if __name__ == "__main__":
    if platform.system() != "Windows":
        raise SystemExit("只支持 Windows 平台")

    data = ReversiData()

    gui = ReversiGUI()

    total_Time = 0

    gui.mainloop()
