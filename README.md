# ReversiAI

使用 MCTS 算法实现黑白棋 Al 棋手

## 快速上手

```
git clone https://github.com/jklincn/ReversiAI
cd ReversiAI
python main.py
```

## 数据结构

### ReversiGUI

用于绘制和管理图形化界面。主要界面有 board（棋盘）和 info（信息输出区域）。

方法：

- \_\_init\_\_：初始化 tkinter 图形化界面，创建 board 和 info，注册鼠标事件，输出初始化信息。
- draw：棋盘绘制函数，用在初始化时和落子后。

### ReversiData

用于控制棋局状态，包括当前棋子数量和位置、落子状态等。

方法：

- \_\_init\_\_：初始化棋局。

---
---

## 功能函数

### click_left

处理鼠标左键点击事件，用于玩家落子。无返回值。

### click_right

处理鼠标左键点击事件，用于玩家重置棋局。无返回值。

### candidate_position

寻找当前棋局可能的落子位置（根据 ReversiData 判断下一步棋是黑棋还是白棋）。返回 Position 数组。

### is_valid_move
根据形参返回此位置是否可以落子，判断依据为黑白棋规则