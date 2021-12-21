# %%

import collections
import pytest
import pandas as pd
import src.datadelta as delta
import importlib
importlib.reload(delta)


# %%


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


@pytest.fixture
def equalDataframesCase():
    old_df = pd.read_csv('src/datadelta/data/EqualDataFrames_old_df.csv')
    new_df = pd.read_csv('src/datadelta/data/EqualDataFrames_new_df.csv')
    primary_key = 'A'
    column_subset = None
    consolidated_report, record_changes_comparison_df = delta.create_consolidated_report(
        old_df, new_df, primary_key, column_subset)
    return [consolidated_report, record_changes_comparison_df]


@pytest.fixture
def removedColumnsCase():
    old_df = pd.read_csv('src/datadelta/data/RemovedColumns_old_df.csv')
    new_df = pd.read_csv('src/datadelta/data/RemovedColumns_new_df.csv')
    primary_key = 'A'
    column_subset = None
    consolidated_report, record_changes_comparison_df = delta.create_consolidated_report(
        old_df, new_df, primary_key, column_subset)
    return [consolidated_report, record_changes_comparison_df]


@pytest.fixture
def mainTestCase():
    old_df = pd.read_csv('src/datadelta/data/MainTestData_old_df.csv')
    new_df = pd.read_csv('src/datadelta/data/MainTestData_new_df.csv')
    primary_key = 'A'
    column_subset = None
    consolidated_report, _ = delta.create_consolidated_report(
        old_df, new_df, primary_key, column_subset)
    consolidated_report.pop('meta')
    consolidated_report = flatten(consolidated_report)

    correct_consolidated_report = delta.load_pickle(
        'src/datadelta/data/correct_consolidated_report.pickle')
    correct_consolidated_report.pop('meta')
    correct_consolidated_report = flatten(correct_consolidated_report)

    return [consolidated_report, correct_consolidated_report]


@pytest.fixture
def columnSubsetCase():
    old_df = pd.read_csv('src/datadelta/data/MainTestData_old_df.csv')
    new_df = pd.read_csv('src/datadelta/data/MainTestData_new_df.csv')
    primary_key = 'A'
    column_subset = ['C', 'D', 'I']
    consolidated_report, _ = delta.create_consolidated_report(
        old_df, new_df, primary_key, column_subset)
    consolidated_report.pop('meta')
    consolidated_report = flatten(consolidated_report)

    correct_consolidated_report = delta.load_pickle(
        'src/datadelta/data/correct_column_subset_report.pickle')
    correct_consolidated_report.pop('meta')
    correct_consolidated_report = flatten(correct_consolidated_report)

    return [consolidated_report, correct_consolidated_report]


class TestDataDelta:
    def test_equal_dataframes(self, equalDataframesCase):
        assert equalDataframesCase[0]['meta']['is_all_equal'] == True
        assert equalDataframesCase[0]['column_name_changes']['is_equal'] == True
        assert equalDataframesCase[0]['datatype_changes']['is_equal'] == True
        assert equalDataframesCase[0]['record_count_changes']['is_equal'] == True
        assert equalDataframesCase[0]['record_value_changes']['is_equal'] == True
        assert equalDataframesCase[1] is None

    def test_removed_columns(self, removedColumnsCase):
        assert removedColumnsCase[0]['meta']['is_all_equal'] == False
        assert removedColumnsCase[0]['column_name_changes']['is_equal'] == False
        assert set(removedColumnsCase[0]['column_name_changes']['values']['removed_columns']) == set([
            'C', 'D'])
        assert removedColumnsCase[0]['datatype_changes']['is_equal'] == True
        assert removedColumnsCase[0]['record_count_changes']['is_equal'] == True
        assert removedColumnsCase[0]['record_value_changes']['is_equal'] == True
        assert removedColumnsCase[1] is None

    def test_main_case(self, mainTestCase):
        # Assert keys match
        assert mainTestCase[0].keys() == mainTestCase[1].keys()

        # Loop through keys and ensure that values match
        different_columns = []

        for key in mainTestCase[1].keys():
            if isinstance(mainTestCase[1][key], pd.DataFrame):
                if not (mainTestCase[0][key].equals(mainTestCase[1][key])):
                    different_columns.append(key)

            else:
                if mainTestCase[0][key] != mainTestCase[1][key]:
                    different_columns.append(key)

        assert len(different_columns) == 0

    def test_column_subset_case(self, columnSubsetCase):
        # Assert keys match
        assert columnSubsetCase[0].keys() == columnSubsetCase[1].keys()

        # Loop through keys and ensure that values match
        different_columns = []

        for key in columnSubsetCase[1].keys():
            if isinstance(columnSubsetCase[1][key], pd.DataFrame):
                if not (columnSubsetCase[0][key].equals(columnSubsetCase[1][key])):
                    different_columns.append(key)

            else:
                if columnSubsetCase[0][key] != columnSubsetCase[1][key]:
                    different_columns.append(key)

        assert len(different_columns) == 0
