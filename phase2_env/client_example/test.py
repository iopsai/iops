import torch
import sys
import logging
import dill
import os
import json


logging.basicConfig(
    level='DEBUG',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__file__)


def main():
    persist = sys.argv[1]
    kpi_id = sys.argv[2]
    logger.info("KPI:" + kpi_id)
    print("IOPS Phase2 Test Ready", flush=True)
    with open(os.path.join(persist, "random.dill"), "rb") as f:
        sign = 1 if torch.sum(dill.load(f)) >= 0. else -1
    for line in sys.stdin:
        logger.info("Client Recv: {}".format(line))
        if "KPI FINISH" in line:
            break
        timestamp, value = line.split(",")
        timestamp = int(timestamp)
        value = float(value)
        logger.info("Timestamp: {}, Value: {}".format(timestamp, value))
        ret = sign * int(value >= 0.0)
        print(ret, flush=True)
        logger.info("Client Send: {}".format(ret))


if __name__ == '__main__':
    main()
