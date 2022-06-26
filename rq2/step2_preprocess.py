from __future__ import annotations

import os
import string
from pathlib import Path

import pandas
from nltk import SnowballStemmer
from nltk.corpus import stopwords

from rq2.utils import pmap, tq
from step1_data_collection import apps


def camel_split(camel: str) -> list[str]:
    """
    Split camel case string into sentence

    Credit: https://stackoverflow.com/a/58996565/7346633

    :param camel: E.g. HelloWorld or helloWorld
    :return: E.g. ['Hello', 'World']
    """
    # Ignore all caps or all lower
    if camel.isupper() or camel.islower() or camel.isnumeric():
        return [camel]

    idx = list(map(str.isupper, camel))

    # Mark change of case
    word = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            word.append(i)
        elif not x and y:  # "lU"
            word.append(i + 1)
    word.append(len(camel))

    # for "lUl", index of "U" will pop twice, have to filter that
    return [camel[x:y] for x, y in zip(word, word[1:]) if x < y]


english_stop_words = {s.lower() for s in stopwords.words('english')}

# Java keywords list from https://docs.oracle.com/javase/tutorial/java/nutsandbolts/_keywords.html
java_stop_words = {
    'abstract', 'continue', 'for', 'new', 'switch',
    'assert', 'default', 'goto', 'package', 'synchronized',
    'boolean', 'do', 'if', 'private', 'this',
    'break', 'double', 'implements', 'protected', 'throw',
    'byte', 'else', 'import', 'public', 'throws',
    'case', 'enum', 'instanceof', 'return', 'transient',
    'catch', 'extends', 'int', 'short', 'try',
    'char', 'final', 'interface', 'static', 'void',
    'class', 'finally', 'long', 'strictfp', 'volatile',
    'const', 'float', 'native', 'super', 'while',

    # Not keywords but still commonly used in java
    'String', 'Integer'
}


def java_stop_word_removal(words: list[str]) -> list[str]:
    """
    Remove stop words including Java keywords
    """
    words = [w for w in words if w.lower() not in english_stop_words]
    words = [w for w in words if w not in java_stop_words]
    return words


stemmer = SnowballStemmer("english")


def pre_process_file_content(content: str) -> str:
    """
    Preprocess content of an entire file
    """
    # Collapse line breaks
    content = content.replace('\n', ' ')

    # Replace symbols with ' '
    content = ''.join([c if c not in string.punctuation else ' ' for c in content])

    # Remove multiple spaces
    while '  ' in content:
        content = content.replace('  ', ' ')

    # Camel case splitting
    word_list = [sw for w in content.split() for sw in camel_split(w)]

    # Remove stop words
    word_list = java_stop_word_removal(word_list)

    # Stem words
    word_list = [stemmer.stem(w) for w in word_list]

    # Join
    content = ' '.join(word_list)

    return content


def pre_process_file(fp: Path):
    """
    Preprocess one file and write the processed content to {file_name}.proc.txt
    """
    fp.with_name(f'{fp.name}.proc.txt').write_text(pre_process_file_content(fp.read_text('utf-8')), 'utf-8')


def pre_process_all_data(in_dir: Path):
    """
    Preprocess all files under a directory
    """
    # Find all java and xml files.
    files = [Path(dp) / f for dp, dn, filenames in os.walk(in_dir) for f in filenames
             if f.lower().endswith('.java') or f.lower().endswith('.xml')]

    # Loop through all files, preprocess them
    pmap(pre_process_file, files)


def pre_process_all_reviews(csv_path: Path):
    """
    Preprocess reviews.csv
    """
    reviews = pandas.read_csv(csv_path).to_dict('records')

    # Include only reviews for apps that have identifiable source code
    reviews = [r for r in reviews if r['app'] in apps and apps[r['app']]]

    for r in tq(reviews, 'Processing reviews'):
        # Include app package names to reviews
        r['pkg'] = apps[r['app']][1]

        # Pre-process review text
        r['reviewTextProc'] = pre_process_file_content(r['reviewText'])

    pandas.DataFrame(reviews).to_csv(csv_path.with_suffix('.processed.csv'))


if __name__ == '__main__':
    print('Pre-processing all .java and .xml files and saving them to {file_name}.txt files in their directories...')
    pre_process_all_data(Path('data'))
    pre_process_all_reviews(Path('reviews.csv'))
