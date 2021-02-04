## 文件说明

"base_game.py"包含了棋盘、游戏server的设计。其中棋盘类包括了生成着法、评估函数的设计。

"minmax.py"中包含了对于alpha-beta剪枝算法的实现、基于zobrist哈希置换表的实现。

"play.py"为运行五子棋的代码文件，在命令行中使用命令：

```
python play.py
```

即可运行五子棋测试。若要修改agent的深度（默认为4，此时棋力已经很不错，并且行棋时间能够控制在3s内），可以参考"play.py"中run函数的注释；若要使用前向剪枝，可以参考"base_game.py"第152行的注释。