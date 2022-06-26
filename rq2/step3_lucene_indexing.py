from __future__ import annotations

import os
from pathlib import Path

import lucene
import pandas
from lupyne import engine
from lupyne.engine import Field
from typing_extensions import Literal

from step1_data_collection import apps_package_map
from step2_preprocess import pre_process_file_content
from org.apache.lucene.search import similarities
from utils import tq


def structure_category(content: str, path: Path) -> Literal['UI', 'Android Manifest', 'Content Provider', 'Service'] | None:
    """
    Obtain structural category of a file, with rules defined in Table III of the paper.
    """
    c = content.lower()
    p = str(path).lower()

    if any(k in p for k in ['res', 'resources', 'ui', 'activity']):
        return 'UI'
    if 'androidmanifest' in p:
        return 'Android Manifest'
    if any(k in c for k in ['content', 'provider']):
        return 'Content Provider'
    if 'service' in p:
        return 'Service'
    return None


class MyIndexer:
    indexer: engine.Indexer

    def __init__(self, app: str):
        lucene.initVM()
        self.index(app)
        print()

    def index(self, app_pkg: str):
        """
        Index for a specific app

        :param app_pkg: Package name of the app
        """
        app_name = apps_package_map[app_pkg]
        dp = f'lucene-data/app-index/{app_pkg}'

        # Already indexed
        indexed = os.path.isdir(dp) and len(os.listdir(dp)) > 0

        # Create indexer
        indexer = engine.Indexer(dp)
        print(similarities)
        indexer.indexSearcher.similarity = similarities.TFIDFSimilarity()
        indexer.set('path', stored=True)
        indexer.set('text', engine.Field.Text)
        indexer.set('structure_category', engine.Field.Text)
        # indexer.fields['structure_category'] = engine.Field.Text('structure_category', boost=0.3)

        if indexed:
            self.indexer = indexer
            return

        # Index source code files
        # Find all java and xml files.
        files = [Path(dp) / f for dp, dn, filenames in os.walk(f'data/{app_pkg}')
                 for f in filenames if f.endswith('.proc.txt')]
        for fp in tq(files, 'Indexing source code'):
            content = fp.read_text('utf-8')
            data = {'path': str(fp), 'text': content}

            sc = structure_category(content, fp)
            if sc:
                data['structure_category'] = sc

            indexer.add(**data)

        indexer.add(path='Test', text='crash')
        indexer.commit()

        # Index reviews
        reviews = pandas.read_csv('reviews.csv').to_dict('records')
        reviews = [r for r in reviews if r['app'] == app_name]
        for r in tq(reviews, 'Indexing reviews'):
            # TODO: Replace with review pre-processing
            text = pre_process_file_content(r['reviewText'])

            if text.strip() == '':
                continue

            indexer.add(path=f"Review {r['_id']}", text=text)
            # print(text)

        self.indexer = indexer
        return

    def search(self, review: str):
        """
        Search for a specific string with pre-processing
        """
        review = pre_process_file_content(review)
        return self.indexer.indexSearcher.search(f'text:"{review}"')


if __name__ == '__main__':
    print(pre_process_file_content("Doesn't work with fingerprint"))
    # idx = MyIndexer('com.achep.acdisplay')
    #
    # # Search test
    # hits = idx.search("Doesn't work with fingerprint")
    # print(len(hits))
    #
    # for i, hit in enumerate(hits[:20]):
    #     print(f'Found #{i} - Score {hit.score:.2f}: {hit["path"]}...')

