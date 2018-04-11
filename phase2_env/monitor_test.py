import click
import subprocess
import logging
import pandas as pd
import numpy as np
import shlex
import sys
import tempfile
import json
from evaluation.evaluation import label_evaluation

DELAY = 7
TIME_LIMIT = 5  # seconds

logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    filename="/var/log/monitor_test.log",
)
logger = logging.getLogger(__file__)


@click.command("Phase2 Test")
@click.option("--config-file-path", "-c", default="", help="Path to config JSON file, leave empty to use stdin")
@click.option("--ground-truth-path", "-g", help="Path to ground truth data, which is supposed to be a hdf file including at least three columns: KPI ID, timestamp, label")
def main(config_file_path, ground_truth_path):
    if config_file_path == "":
        config_file = sys.stdin
    else:
        config_file = open(config_file_path, "r")
    config_list = json.load(config_file)  # type: list
    list(map(lambda team_config: test(ground_truth_path, team_config), config_list))


def test(ground_truth_path, team_config):
    image_name = team_config["uuid"]
    test_command = team_config["test"]
    persist_path = team_config["persist"]

    # read ground truth and prepare dataframe to store predicts
    ground_truth_dataframe = pd.read_hdf(ground_truth_path)
    predict_dataframe_list = []
    kpi_id_list = np.unique(ground_truth_dataframe['KPI ID'].values)

    # main process
    for kpi_id in kpi_id_list:
        logger.info("KPI ID: {}".format(kpi_id))
        # create client subprocess
        command = "sudo nvidia-docker run -i --rm --ipc=host -v {persist}:{persist}:ro {image_name} {command} \"{persist}\" \"{kpi}\"".format(image_name=image_name, command=test_command, kpi=kpi_id, persist=persist_path)
        logging.info("Run command: {}".format(command))
        client = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  universal_newlines=True, bufsize=0)
        logger.info("Create client successfully.")
        while True:
            line = read_non_empty_line(client.stdout)
            line = line.rstrip("\r\n")
            print(line)
            if line == "IOPS Phase2 Test Ready":
                break
        # create dataframe to store predicts
        kpi_predict_dataframe = pd.DataFrame()

        # read ground truth and sort by timestamp in ascending order
        kpi_ground_truth = ground_truth_dataframe[ground_truth_dataframe["KPI ID"] == kpi_id]
        timestamps = np.asarray(kpi_ground_truth["timestamp"], dtype=np.int64)
        values = np.asarray(kpi_ground_truth["value"], dtype=np.float32)
        sort_index = np.argsort(timestamps)
        timestamps = timestamps[sort_index]
        values = values[sort_index]

        predict_list = []
        for timestamp, value in zip(timestamps, values):
            # send timestamp and value
            print("{},{}".format(timestamp, value), file=client.stdin)
            # receive timestamp
            predict = 0
            line = read_non_empty_line(client.stdout)
            line.rstrip("\r\n")
            logger.info("Monitor Receive: {}".format(line))
            try:
                predict = int(line)
            except ValueError:
                logging.error("Parse message as int failed, use default value 0. Recv: {}".format(line))
            predict_list.append(predict)

        kpi_predict_dataframe["timestamp"] = timestamps
        kpi_predict_dataframe["predict"] = np.asarray(predict_list, np.int)
        kpi_predict_dataframe["KPI ID"] = kpi_id
        predict_dataframe_list.append(kpi_predict_dataframe)

        print("KPI FINISH", file=client.stdin)
        client.wait()
    predict_dataframe = pd.concat(predict_dataframe_list)   # type: pd.DataFrame
    predict_file = tempfile.NamedTemporaryFile(suffix=".csv")
    predict_dataframe.to_csv(predict_file.name, index=None)

    result = label_evaluation(ground_truth_path, predict_file.name, delay=DELAY)
    logger.info("Result:" + result)
    return result


def read_non_empty_line(stream):
    while True:
        line = stream.readline()  # type: str
        if line == "":
            continue
        line = line.rstrip("\n")
        if line != "":
            return line


if __name__ == '__main__':
    print(main())
