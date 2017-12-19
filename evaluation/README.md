# Run experiment

python evaluation.py truth.hdf predict.csv 7

parameters:

    truth.hdf: the ground truth file, column names contain KPI ID, timestamp, label

    predict.csv: the results of user submitted, column names contain KPI ID, timestamp, predict
    
    7: delay threshold（暂定)
    

提交的结果可以和给出的测试集顺序不一样，可以通过predict_order_test.csv 和 predict.csv样例自行测试。

注：评估脚本详细说明，请参见http://iops.ai/competition_detail/?competition_id=5&flag=1
    

