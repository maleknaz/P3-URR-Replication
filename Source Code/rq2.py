import pandas as pd


if __name__ == '__main__':
    df = pd.read_csv('linking_data.csv', encoding='ISO-8859-1')
    df['correct_classes'] = ''

    for index, row in df.iterrows():
        s0 = row['linked_classes']
        s1 = row['incorrect_classes']
        s2 = row['missing_classes']
        correct_items = []

        if type(s0) == str:
            s0 = s0.split(' ')
            row['linked_classes'] = s0
        else:
            row['linked_classes'] = []

        if type(s1) == str:
            s1 = s1.split(' ')
            s1 = [x.replace('.', '/', x.count(".") - 1) for x in s1]
            row['incorrect_classes'] = s1
        else:
            row['incorrect_classes'] = []

        if type(s2) == str:
            s2 = s2.split(' ')
            s2 = [x.replace('.', '/', x.count(".") - 1) for x in s2]
            correct_items = s2

        items_to_be_deleted = []
        for l_item in row['linked_classes']:
            for i_item in row['incorrect_classes']:
                if l_item.find(i_item) != -1:
                    items_to_be_deleted.append(l_item)
                    break

        for item in row['linked_classes']:
            if item not in items_to_be_deleted:
                correct_items.append(item)

        row['correct_classes'] = correct_items

    df.drop(columns=['linked_classes', 'incorrect_classes', 'missing_classes', 'linkable'], inplace=True)
    df.to_csv('data.csv', index=False)

    df2 = pd.read_csv('data.csv', encoding='ISO-8859-1')
