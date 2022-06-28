import json
import os
import random
from pathlib import Path


RESULTS_PATH = Path("data-lucene/app-result")


def create_sample(n: int = 100):
    # Combine all apps' search results
    jsons = [RESULTS_PATH / f for f in os.listdir(str(RESULTS_PATH)) if f.endswith('.json')]
    jsons = [item for f in jsons for item in json.loads(f.read_text())]

    # Randomly select a sample of n
    sample = random.sample(jsons, n)

    # Store sample
    Path(f"data-lucene/app-result-sample-{n}.json").write_text(json.dumps(sample, indent=2))


if __name__ == '__main__':
    create_sample()
