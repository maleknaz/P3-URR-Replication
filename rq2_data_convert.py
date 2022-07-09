import math
from pathlib import Path

import pandas


def normalize_linked_class(p: str) -> str:
    p = p.replace('/a_comic_viewer/droid-comic-viewer-master/src/', '') \
        .replace('/acdisplay/AcDisplay-master/project/app/src/', '')\
        .replace('master/project/app/src/', '')\
        .replace('main/java/', '')\
        .replace('main/', '')

    # Manual evaluator's typo
    p = p.replace('Permisssion', 'Permission')

    if p.endswith('.java'):
        p = p.replace('/', '.')

    # Manual evaluator's typo
    if p == 'com.achep.base.utils.zen.ZenUtils':
        p = 'com.achep.base.utils.zen.ZenUtils.java'

    return p



if __name__ == '__main__':
    df = pandas.read_csv(Path('Data/RQ_2/linking_data-and-results.csv')).to_dict('records')

    for d in df:
        for k in ['missing_classes', 'incorrect_classes']:
            if isinstance(d[k], float):
                d[k] = ''

        lc = d['linked_classes'] = [normalize_linked_class(f) for f in d['linked_classes'].split()]
        ic = d['incorrect_classes'] = [normalize_linked_class(f) for f in d['incorrect_classes'].split()]
        mc = d['missing_classes'] = [normalize_linked_class(f) for f in d['missing_classes'].split()]
        cc = d['correct_classes'] = mc + [f for f in lc if f not in ic]

        # All incorrect classes must be in linked classes, or else they shouldn't be incorrect
        # assert all(f in lc for f in ic)
        # All missing classes must not be in linked classes
        # assert all(f not in lc for f in mc)
        # TP, FP, FN
        # assert int(d['TP']) == len(lc) - len(ic)
        # assert int(d['FP']) == len(ic)
        # assert int(d['FN']) == len(mc)

    pandas.DataFrame(df).to_csv('Data/RQ_2/linking_data_processed.csv', index=False)
