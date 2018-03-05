# 决赛评估环境

为了比赛公正，决赛需要由主办方运行选手的程序得到结果。
具体的形式是，决赛期间我们为每个队伍分配一定金额的Azure订阅，每支队伍自行创建虚拟机并按下文的要求调试运行环境（具体来说就是一个包含了选手程序的Docker Image），然后主办方会使用Azure的计算资源运行每支队伍的程序得到评测结果。

# 选手需要准备的内容

- 一个Docker context(一个文件夹)，包含了选手的程序和Dockerfile。
  请确保在Dockerfile中将Context中必要的程序文件拷贝到Docker镜像的合适的位置
- 在给出的Docker镜像中启动训练和测试程序所用的命令。以如下格式存放在Docker context文件夹的"config.json"文件中

```json
{
    "team": ${队伍名，如"railgun"}
    "train": ${训练程序命令，如"python train.py"},
    "test": ${测试程序命令，如"python test.py"},
}
```

请参考`client_example` 

在当前目录运行`test.sh`，并且把Docker Context文件夹放在这里（和`client_example`同级），可以测试是否能够正确运行

# 主办方操作流程

1. 把选手准备好的Docker Context文件夹拷贝到新虚拟机的某个目录下

2. 检查每个选手的Dockerfile，主要针对可能的作弊行为。

3. 编译Docker镜像，准备每个选手会用到的可写入路径等资源

   ```bash
   python build_env.py -b ${存放context文件夹的目录} -o ${输出配置文件路径}
   ```

   输出文件是一个JSON文件，包含每个队伍的队名，镜像名，操作命令，存储路径等信息。

4. 训练

   ```bash
   python monitor_train.py -c ${配置文件路径} -t ${训练数据路径}
   ```

   训练数据是一个HDF文件，包含了所有KPI的时间戳，值，名字等信息。

5. 测试

   ```bash
   python monitor_test.py -c ${配置文件路径} -t ${Ground Truth路径}
   ```

   测试数据是一个HDF文件，包含了所有KPI的时间戳，标注，名字等信息。

# 训练流程

1. 通过Docker启动选手程序， 包含如下两个命令行参数
   1. 一个**可写入并持久保存**（在测试时可用）的路径，可将训练好的模型文件等存储在这里
   2. 训练数据文件的路径，所有KPI的数据都在这一个文件中。格式是CSV，和预赛阶段的格式相同

# 测试流程

对于每一条KPI:

1. 通过Docker启动选手程序，包含如下两个命令行参数
   1. 一个**只读**的路径（和训练时给出的用于持久保存地址相同）
   2. KPI ID
2. 等待选手程序在标准输出发送一行: "IOPS Phase2 Test Ready"。 请选手注意务必刷新输出缓冲区
3. 向选手程序依序发送一个KPI数据点的时间戳和值。 一行逗号分隔的两个值，时间戳(long int)和KPI值(float): timestamp,value
4. 从选手程序的标准输出获取检测结果。一行，只有一个整数，0或者1。 选手程序需要注意及时刷新输出缓冲区
5. 重复3~4直到这条KPI所有数据点都检测完成。
6. 发送一行：KPI FINISH。选手需要在接收到这一行之后退出测试程序

