#!/usr/bin/env python
# encoding: utf-8

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier


def names(train, test):
    for i in [train, test]:
        i['Name_Len'] = i['Name'].apply(lambda x: len(x))
        i['Name_Title'] = i['Name'].apply(lambda x: x.split(',')[1]).apply(lambda x: x.split()[0])
        del i['Name']
    return train, test


def age_impute(train, test):
    for i in [train, test]:
        i['Age_Null_Flag'] = i['Age'].apply(lambda x: 1 if pd.isnull(x) else 0)
        data = train.groupby(['Name_Title', 'Pclass'])['Age']
        i['Age'] = data.transform(lambda x: x.fillna(x.mean()))
    return train, test


def fam_size(train, test):
    for i in [train, test]:
        i['Fam_Size'] = np.where((i['SibSp'] + i['Parch']) == 0, 'Solo',
                                 np.where((i['SibSp'] + i['Parch']) <= 3, 'Nuclear', 'Big'))
        del i['SibSp']
        del i['Parch']
    return train, test


def ticket_grouped(train, test):
    for i in [train, test]:
        i['Ticket_Lett'] = i['Ticket'].apply(lambda x: str(x)[0])
        i['Ticket_Lett'] = i['Ticket_Lett'].apply(lambda x: str(x))
        i['Ticket_Lett'] = np.where((i['Ticket_Lett']).isin(['1', '2', '3', 'S', 'P', 'C', 'A']), i['Ticket_Lett'],
                                    np.where((i['Ticket_Lett']).isin(['W', '4', '7', '6', 'L', '5', '8']), 'Low_ticket', 'Other_ticket'))
        i['Ticket_Len'] = i['Ticket'].apply(lambda x: len(x))
        del i['Ticket']
    return train, test


def cabin_num(train, test):
    for i in [train, test]:
        i['Cabin_num1'] = i['Cabin'].apply(lambda x: str(x).split(' ')[-1][1:])
        i['Cabin_num1'].replace('an', np.NaN, inplace=True)
        # i['Cabin_num1'] = i['Cabin_num1'].apply(lambda x: int(x) if not pd.isnull(x) and x!=' ' else np.NaN)
        i['Cabin_num1'] = i['Cabin_num1'].apply(lambda x: int(x) if not pd.isnull(x) and x!='' else np.NaN)
        i['Cabin_num'] = pd.qcut(train['Cabin_num1'], 3)
    train = pd.concat((train, pd.get_dummies(train['Cabin_num'], prefix='Cabin_num')), axis=1)
    test = pd.concat((test, pd.get_dummies(test['Cabin_num'], prefix='Cabin_num')), axis=1)
    del train['Cabin_num']
    del test['Cabin_num']
    del train['Cabin_num1']
    del test['Cabin_num1']
    return train, test


def cabin(train, test):
    for i in [train, test]:
        i['Cabin_Letter'] = i['Cabin'].apply(lambda x: str(x)[0])
        del i['Cabin']
    return train, test


def embarked_impute(train, test):
    for i in [train, test]:
        i['Embarked'] = i['Embarked'].fillna('S')
    return train, test


def fare_impute(train, test):
    for i in [train, test]:
        i['Fare'].fillna(i['Fare'].mean(), inplace=True)
    return train, test


def dummies(train, test, columns=['Pclass', 'Sex', 'Embarked', 'Ticket_Lett', 'Cabin_Letter', 'Name_Title', 'Fam_Size']):
    for column in columns:
        train[column] = train[column].apply(lambda x: str(x))
        test[column] = test[column].apply(lambda x: str(x))
        good_cols = [column + '_' + i for i in train[column].unique() if i in test[column].unique()]
        train = pd.concat((train, pd.get_dummies(train[column], prefix=column)[good_cols]), axis=1)
        test = pd.concat((test, pd.get_dummies(test[column], prefix=column)[good_cols]), axis=1)
        del train[column]
        del test[column]
    return train, test


def drop(train, test, bye=['PassengerId']):
    for i in [train, test]:
        for z in bye:
            del i[z]
    return train, test


def handle_data():
    train = pd.read_csv(os.path.join('input/', 'train.csv'))
    test = pd.read_csv(os.path.join('input/', 'test.csv'))
    train, test = names(train, test)
    train, test = age_impute(train, test)
    train, test = fam_size(train, test)
    train, test = ticket_grouped(train, test)
    train, test = cabin_num(train, test)
    train, test = cabin(train, test)
    train, test = embarked_impute(train, test)
    train, test = fare_impute(train, test)
    train, test = dummies(train, test, columns=['Pclass', 'Sex', 'Embarked', 'Ticket_Lett', 'Cabin_Letter', 'Name_Title', 'Fam_Size'])
    train, test = drop(train, test)

    print train
    print train.info()

    # print test
    # print test.info()

    # print (len(train.columns))
    return train, test


if __name__ == '__main__':
    train, test = handle_data()

    rf = RandomForestClassifier(criterion='gini', 
                             n_estimators=50,
                             min_samples_split=10,
                             min_samples_leaf=1,
                             max_features='auto',
                             oob_score=True,
                             random_state=1,
                             n_jobs=-1)
    rf.fit(train.iloc[:, 1:], train.iloc[:, 0])
    print("%.4f" % rf.oob_score_)
    predictions = rf.predict(test)
    predictions = pd.DataFrame(predictions, columns=['Survived'])
    test = pd.read_csv(os.path.join('input/', 'test.csv'))
    predictions = pd.concat((test.iloc[:, 0], predictions), axis = 1)
    predictions.to_csv('Titanic_RandomForest.csv', sep=",", index = False)

    # print(gs.bestscore)
    # print gs.bestparams
    # print gs.cvresults
    # print gs
