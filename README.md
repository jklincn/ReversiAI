# ReversiAI

使用 MCTS 算法实现黑白棋 Al 棋手

## 算法流程
- 整体大循环模拟次数：
    - 选择 Selection：
        - 根据UCB算法递归选择子节点
        - 返回子节点序列
    - 根据子节点序列更新棋盘
    - 扩展 Expansion：
        - 根据合法子节点扩展子节点
    - 模拟 Simluation：
        - 随机选择合法子节点下棋
        - 返回模拟结局(True/False)
    - 回溯 Backpropagation：
        - 自顶向下传递参数
        - 更新结点的reward
- 选择下一步棋位置：
    - 循环遍历合法子节点
        - 选择reward最大的子节点

## 快速上手

```
git clone https://github.com/jklincn/ReversiAI
cd ReversiAI
python main.py
```
