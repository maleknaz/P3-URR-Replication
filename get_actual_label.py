import os
from pathlib import Path

import pandas as pd


def get_actual_label(predicted: int, correct: int) -> int:
    return int(predicted if correct else not predicted)


if __name__ == '__main__':
    os.chdir('Data')
    out_dir = Path('RQ_1_mod')
    out_dir.mkdir(exist_ok=True)

    for d in ['RQ_1/high', 'RQ_1/low']:
        for f in [f for f in os.listdir(d) if 'ERROR' not in f]:
            df = pd.read_csv(Path(d) / f, encoding='ISO-8859-1')
            df['Actual Label'] = df.apply(lambda x: get_actual_label(x[2], x[3]), axis=1)
            df.to_csv(out_dir / f, index=False)
