import torch
import sys
import logging


logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=open("/home/v-zyl14/iops/phase2_env/log.txt", "w+"),
)


def anomaly_detect(kpi_id):
    while True:
        line = sys.stdin.readline()  # type: str
        line = line.rstrip("\r\n")
        logging.info("Receive:" + line)
        if line == "KPI FINISH":  # KPI Finished
            break

        obj = eval(line)
        _ = obj["timestamp"]
        _ = obj["value"]

        # not meaningful
        tensor = torch.randn(100, 100).cuda()  # test GPU support
        predict = int(torch.sum(tensor) > 0.)
        print({"predict": predict})
        sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.rstrip("\r\n")
        logging.info("Receive:" + line)
        if line == "":  # EOF
            break
        if line == "EXIT":  # All KPI Finished
            break

        obj = eval(line)
        if "KPI ID" in obj:
            anomaly_detect(obj["KPI ID"])


if __name__ == '__main__':
    main()
