import sys
import torch
import pandas as pd
import os
import dill


def main():
    persist_path = sys.argv[1]
    train_data_path = sys.argv[2]

    df = pd.read_csv(train_data_path)

    # test read train data file
    kpi_ids = list(set(df["KPI ID"]))
    print("kpi_id:", kpi_ids)

    # test GPU operation
    torch.randn(200, 200).cuda() @ torch.randn(200, 200).cuda()

    # test filesystem write operation
    with open(os.path.join(persist_path, "random.dill"), "wb+") as f:
        dill.dump(torch.randn(100, 100), file=f)


if __name__ == '__main__':
    main()