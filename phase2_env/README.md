# 决赛评估环境

决赛会为每位选手提供一台虚拟机，为了保证测试时不会用到未来数据，所以需要要求选手程序给出一个点的检测结果之后才能得到下一个点的值。
选手需要在虚拟机上按要求配置好测试程序和Docker环境。

# 评估脚本流程
1. 通过Docker启动选手程序
2. 向选手程序的标准输入发送一个KPI点的时间和值。
3. 从选手程序的标准输出获取检测结果
4. 重复2~3直到所有数据都已发送

运行示例
``` bash
PYTHONPATH=$(realpath ..) python monitor.py -i iops-client -c 'python client.py' -f example_ground_truth.hdf
```

# 选手需要准备的内容
一个Docker镜像，其中包含了可以完成KPI异常检测（仅需要包含测试部分，不训练）的程序和运行环境
参考`client_example`