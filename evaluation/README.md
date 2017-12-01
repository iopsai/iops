# Run experiment

python evaluation.py 'ground_truth.hdf' 'predict.csv' 7

parameters:

    ground_truth.hdf: the ground truth file, column names contain KPI ID, timestamp, label

    predict.csv: the results of user submitted, column names contain KPI ID, timestamp, predict
    
    7: delay threshold（暂定)
    


注：评估脚本详细说明，请参见http://iops.ai/competition_detail/?competition_id=5&flag=1
    

