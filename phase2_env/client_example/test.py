import torch
import sys
import dill
import os
import json

def main():
    persist = sys.argv[1]
    kpi_id = sys.argv[2]
    print("IOPS Phase2 Test Ready", flush=True)
    with open(os.path.join(persist, "random.dill"), "rb") as f:
        sign = 1 if torch.sum(dill.load(f)) >= 0. else -1
    for line in sys.stdin:
        if "KPI FINISH" in line:
            break
        timestamp, value = line.split(",")
        timestamp = int(timestamp)
        value = float(value)
        ret = sign * int(value >= 0.0)
        ret = int(ret > 0)
        print(ret, flush=True)


if __name__ == '__main__':
    main()
