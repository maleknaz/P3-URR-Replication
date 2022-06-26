import pandas as pd


if __name__ == '__main__':
    df = pd.read_csv('new_golden.csv')

    count = 0
    usage = ['APP USABILITY', 'UI']
    compatibility = ['DEVICE', 'ANDROID VERSION', 'HARDWARE']
    resources = ['PERFORMANCE', 'BATTERY', 'MEMORY']
    pricing = ['LICENSING', 'PRICE']
    protection = ['PRIVACY', 'SECURITY']
    temp = []
    temp2 = []
    for index, row in df.iterrows():

        low_level_cat = set()
        if not pd.isnull(row['class1']) and row['class1'] != "ERROR":
            low_level_cat.add(row['class1'])
        if not pd.isnull(row['class2']) and row['class2'] != "ERROR":
            low_level_cat.add(row['class2'])
        if not pd.isnull(row['class3']) and row['class3'] != "ERROR":
            low_level_cat.add(row['class3'])

        high_level_cat = set()
        if row['class1'] in usage:
            high_level_cat.add('USAGE')
        elif row['class1'] in compatibility:
            high_level_cat.add('COMPATIBILITY')
        elif row['class1'] in resources:
            high_level_cat.add('RESSOURCES')
        elif row['class1'] in pricing:
            high_level_cat.add('PRICING')
        elif row['class1'] in protection:
            high_level_cat.add('PROTECTION')

        if row['class2'] in usage:
            high_level_cat.add('USAGE')
        elif row['class2'] in compatibility:
            high_level_cat.add('COMPATIBILITY')
        elif row['class2'] in resources:
            high_level_cat.add('RESSOURCES')
        elif row['class2'] in pricing:
            high_level_cat.add('PRICING')
        elif row['class2'] in protection:
            high_level_cat.add('PROTECTION')

        if row['class3'] in usage:
            high_level_cat.add('USAGE')
        elif row['class3'] in compatibility:
            high_level_cat.add('COMPATIBILITY')
        elif row['class3'] in resources:
            high_level_cat.add('RESSOURCES')
        elif row['class3'] in pricing:
            high_level_cat.add('PRICING')
        elif row['class3'] in protection:
            high_level_cat.add('PROTECTION')

        if len(high_level_cat) == 0:
            temp.append([])
        else:
            li = list(high_level_cat)
            temp.append(li)

        if len(low_level_cat) == 0:
            temp2.append([])
        else:
            lis = list(low_level_cat)
            temp2.append(lis)


    df.insert(loc=1, column="new_HLC", value=temp)
    df.insert(loc=2, column="new_LLC", value=temp2)

    df.to_csv('new_golden.csv')
