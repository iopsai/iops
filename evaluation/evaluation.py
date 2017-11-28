import numpy as np
import pandas as pd
import json
from sys import argv
from sklearn.metrics import precision_score,recall_score,f1_score

# consider delay threshold and missing segments

def get_range_proba(predict, label, delay=7):

    splits = np.where(label[1:] != label[:-1])[0] + 1
    is_anomaly = label[0] == 1
    new_predict = np.array(predict)
    pos = 0
    for sp in splits:
        if is_anomaly and 1 in predict[pos:pos+delay+1]:
            new_predict[pos: sp] = np.max(predict[pos: sp])
        is_anomaly = not is_anomaly
        pos = sp
    sp = len(label)
    if is_anomaly:
        new_predict[pos: sp] = np.max(predict[pos: sp])
    return new_predict


def label_evaluation(truth_file, result_file, delay=7):
    # have missing timestamps

    data = {'result': False, 'data': "", 'message': ""}
    try:
        if result_file[-4:]!='.csv':
            data['message'] = 'The file you submitted must be .csv'
            return json.dumps(data)
        else:
            result_df = pd.read_csv(result_file)
    except Exception as e:
        data['message'] =str(e)
        return json.dumps(data)

    truth_df = pd.read_hdf(truth_file)
    truth = truth_df['label'].values
    ts = truth_df['timestamp'].values

    try:
        predict = result_df['predict'].values
        predict_ts = result_df['timestamp'].values
    except Exception as e:
        data['message'] = "The file you submitted need contain 'predict' and 'timestamp' columns"
        return json.dumps(data)

    try:
        assert np.array_equal(ts,predict_ts) == True
    except:
        data['message'] = "The timestamps of your submitted result are wrong"
        return json.dumps(data)


    interval = ts[1] - ts[0]
    start_ts = ts[0]
    end_ts = ts[-1]
    index = 0

    # the labels of missing points are set to zero
    predict_list = list(predict)
    truth_list = list(truth)

    for i in range(start_ts,end_ts,interval):
        if (i not in ts):
            predict_list.insert(index,0)
            truth_list.insert(index,0)
        index += 1

    predict = np.array(predict_list)
    truth = np.array(truth_list)


    new_predict = get_range_proba(predict,truth,delay)
    fscore = f1_score(truth,new_predict)
    data['result'] = True
    data['data'] = fscore
    data['message'] = 'success'
    return json.dumps(data)

if __name__ == '__main__':

    _,truth_file,result_file,delay = argv
    delay = (int)(delay)
    print(label_evaluation(truth_file,result_file,delay))

# run example:
# python evaluation.py 'ground_truth.csv' 'predict.csv' 2
