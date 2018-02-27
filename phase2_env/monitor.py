"""
Working Process:
    (bounding quotes is not included.)
    ("${}" means the corresponding value)
    (lines separator is \n)
    While there are KPIs:
        Send one line: "{'KPI ID':'${KPI ID}'}"
        While there are points in this KPI:
            Send one line: "{"timestamp": ${timestamp}, "value": ${value}}"
            Wait one line in this format: "{"predict": ${predict, 0 for normal, 1 for anomaly}}".
            If get wrong format or time limit exceed, MONITOR will ignore it and assume the predict is 0, then continue.
        Send one line: "KPI FINISH"
    Send on line "EXIT"
"""
import click
import subprocess
import logging
import pandas as pd
import numpy as np
import shlex
import sys
import tempfile
from evaluation.evaluation import label_evaluation

TIME_LIMIT = 5  # seconds
DELAY = 7
COMMAND = "sudo nvidia-docker run -i --rm --ipc=host -v /home/v-zyl14/:/home/v-zyl14 {image_name} {command}"

logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__file__)


@click.command("Monitor")
@click.option("--image-name", "-i", help="The docker image name")
@click.option("--client-command", "-c", help="What command to run in the docker container")
@click.option("--ground-truth-path", "-f", help="Path to ground truth file")
def main(image_name, client_command, ground_truth_path):
    # create client subprocess
    command = COMMAND.format(image_name=image_name, command=client_command)
    logging.info("Run command: {}".format(command))
    client = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              universal_newlines=True, bufsize=1)
    logger.info("Create client successfully.")

    # read ground truth and prepare dataframe to store predicts
    ground_truth_dataframe = pd.read_hdf(ground_truth_path)
    predict_dataframe_list = []
    kpi_id_list = np.unique(ground_truth_dataframe['KPI ID'].values)

    # main process
    for kpi_id in kpi_id_list:
        logger.info("KPI ID: {}".format(kpi_id))
        # create dataframe to store predicts
        kpi_predict_dataframe = pd.DataFrame()

        # send KPI ID
        print({"KPI ID": kpi_id}, file=client.stdin)
        client.stdin.flush()

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
            print({"timestamp": timestamp, "value": value}, file=client.stdin)
            client.stdin.flush()
            # receive timestamp
            predict = 0
            try:
                line = read_non_empty_line(client.stdout)
                line.rstrip("\n")
                logger.info("Receive: {}".format(line))
                predict = eval(line)["predict"]
            except KeyError:  # no "predict" key in response
                pass
            except SyntaxError:  # can't eval response as a dict
                pass
            predict_list.append(predict)

        kpi_predict_dataframe["timestamp"] = timestamps
        kpi_predict_dataframe["predict"] = np.asarray(predict_list, np.int)
        kpi_predict_dataframe["KPI ID"] = kpi_id
        predict_dataframe_list.append(kpi_predict_dataframe)
        print("KPI FINISH", file=client.stdin)
        client.stdin.flush()
    print("EXIT", file=client.stdin)
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
