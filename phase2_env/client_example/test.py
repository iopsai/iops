import torch
import sys
import logging
import dill
import os
import json


logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
)
logger = logging.getLogger(__file__)


def main():
    persist = sys.argv[1]
    kpi_id = sys.argv[2]
    logger.info("KPI:" + kpi_id)
    with open(os.path.join(persist, "random.dill"), "rb") as f:
        sign = torch.sum(dill.load(f)) >= 0.
    for line in sys.stdin:
        logger.info("Client Recv: {}".format(line))
        if "KPI FINISH" in line:
            break
        point = json.loads(line)
        ret = json.dumps({"predict": sign * int(point["value"] >= 0.0)})
        print(ret)
        logger.info("Client Send: {}".format(ret))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
