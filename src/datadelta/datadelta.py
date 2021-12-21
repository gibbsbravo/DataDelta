# %%
import pickle
import os
import pandas as pd
import numpy as np
from jinja2 import Template
import collections
from datetime import datetime

pd.set_option('colheader_justify', 'center')

# %% Number of records


def get_df_summary(input_df, primary_key, column_subset, max_cols=15):
    """
    Returns a report summarizing the key attributes and values of a dataframe

    Parameters:
        input_df (pandas dataframe): The pandas dataframe to be summarized
        primary_key (string): The primary key for the table
        max_cols (int): The maximum number of columns included in the summary table

    Returns:
        report (dict): Summary report with key values and dataframe summary
    """

    # Save copy of dataframe to avoid modifying the original dataframe
    input_df = input_df.copy()

    # Instantiate the report
    report = collections.defaultdict(dict)

    assert isinstance(input_df, pd.DataFrame), "Input is not a dataframe"
    assert input_df.empty == False, "Dataframe is empty"

    # Get the number of records and columns
    report['number_of_records'] = len(input_df)
    report['number_of_columns'] = len(input_df.columns)

    # Check if primary key is unique
    report['primary_key'] = primary_key

    if input_df[primary_key].value_counts().max() == 1:
        report['is_primary_key_unique'] = True
    else:
        report['is_primary_key_unique'] = False

    # Get number of null records
    df_summary = input_df.notnull().sum(
        0).reset_index()
    df_summary.rename(columns={"index": "column_names",
                      0: "n_valid_records"}, inplace=True)
    df_summary['prop_valid_records'] = np.around(
        (df_summary['n_valid_records'] / len(input_df)) * 100, 1)

    df_summary = pd.merge(df_summary, input_df.dtypes.to_frame(
        name="datatype"), how='left', left_on='column_names', right_index=True)

    df_summary.sort_values(["n_valid_records", 'column_names'],
                           ascending=[False, True], inplace=True)

    if column_subset is not None:
        df_summary = df_summary.loc[df_summary['column_names'].isin(
            [primary_key] + column_subset)]

    df_summary.reset_index(drop=True, inplace=True)

    # Only show top n columns if number of columns is greater than n
    if len(df_summary) > max_cols:
        report['summary_table'] = df_summary.iloc[:max_cols]

    else:
        report['summary_table'] = df_summary

    return report


def check_column_names(old_df, new_df):
    """
    Returns a report summarizing any changes to column names between two dataframes

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared

    Returns:
        report (dict): Summary report showing the columns changes
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    # Instantiate the report
    report = collections.defaultdict(dict)

    # Check if column names are equal
    if set(old_df.columns) == set(new_df.columns):
        report['column_name_changes']['is_equal'] = True

    else:
        columns_only_in_old = set(old_df.columns) - set(new_df.columns)
        columns_only_in_new = set(new_df.columns) - set(old_df.columns)

        report['column_name_changes']['is_equal'] = False
        report['column_name_changes']['summary'] = []
        report['column_name_changes']['values'] = {}

        if len(columns_only_in_old) > 0:
            report['column_name_changes']['summary'].append(
                "{} Unique column(s) in the old table".format(len(columns_only_in_old)))
            report['column_name_changes']['values']['removed_columns'] = list(
                columns_only_in_old)

        elif len(columns_only_in_new) > 0:
            report['column_name_changes']['summary'].append(
                "{} Unique column(s) in the new table".format(len(columns_only_in_new)))
            report['column_name_changes']['values']['added_columns'] = list(
                columns_only_in_new)
    return report


def check_record_count(old_df, new_df, primary_key):
    """
    Returns a report summarizing any changes to the number of records (and composition) between two dataframes

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        primary_key (string): The primary key for each dataframe (must be the same primary key)

    Returns:
        report (dict): Summary report showing the record count changes and composition
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    # Instantiate the report
    report = collections.defaultdict(dict)

    # Get the record count for each dataframe
    num_old_records = len(old_df)
    num_new_records = len(new_df)

    # Get the IDs that have been removed or added
    removed_ids = set(old_df[primary_key]) - set(new_df[primary_key])
    added_ids = set(new_df[primary_key]) - set(old_df[primary_key])

    if (len(removed_ids) == 0) & (len(added_ids) == 0):
        report['record_count_changes']['is_equal'] = True

    else:
        report['record_count_changes']['is_equal'] = False
        report['record_count_changes']['summary'] = []
        report['record_count_changes']['values'] = {}

        report['record_count_changes']['summary'].append(
            "The old table has {:,} records".format(num_old_records))
        report['record_count_changes']['summary'].append(
            "The new table has {:,} records".format(num_new_records))
        report['record_count_changes']['summary'].append(
            "Change in the total number of records: {:,}".format(num_new_records - num_old_records))

        if len(removed_ids) > 0:
            report['record_count_changes']['summary'].append(
                '{:,} record(s) removed'.format(len(removed_ids)))
            report['record_count_changes']['values']['removed_records'] = list(
                removed_ids)
        if len(added_ids) > 0:
            report['record_count_changes']['summary'].append(
                '{:,} record(s) added'.format(len(added_ids)))
            report['record_count_changes']['values']['added_records'] = list(
                added_ids)

    return report


def get_records_in_both_tables(old_df, new_df, primary_key, column_subset=None):
    """
    Returns the records found in both dataframes

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        primary_key (string): The primary key for each dataframe (must be the same primary key)
        column_subset (list of strings): Default value is None which includes all columns.
            The subset of columns under consideration for the comparison 

    Returns:
        shared_old_df_values (pandas dataframe): A dataframe containing the records shared
             by both dataframes found in the first dataframe
        shared_new_df_values (pandas dataframe): A dataframe containing the records shared
             by both dataframes found in the second dataframe
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    records_in_both_tables = list(
        set(old_df[primary_key]).intersection(set(new_df[primary_key])))
    columns_in_both_tables = list(
        set(old_df.columns).intersection(set(new_df.columns)))

    if column_subset is None:
        shared_old_df_values = old_df.loc[old_df[primary_key].isin(
            records_in_both_tables), columns_in_both_tables].sort_values(primary_key).reset_index(drop=True).fillna("na")
        shared_new_df_values = new_df.loc[new_df[primary_key].isin(
            records_in_both_tables), columns_in_both_tables].sort_values(primary_key).reset_index(drop=True).fillna("na")
    else:
        assert len(np.setdiff1d(column_subset, columns_in_both_tables)) == 0, "{} columns are not contained in both tables".format(
            np.setdiff1d(column_subset, columns_in_both_tables))

        if primary_key not in column_subset:
            column_subset = column_subset + [primary_key]

        shared_old_df_values = old_df.loc[old_df[primary_key].isin(
            records_in_both_tables), column_subset].sort_values(primary_key).reset_index(drop=True).fillna("na")
        shared_new_df_values = new_df.loc[new_df[primary_key].isin(
            records_in_both_tables), column_subset].sort_values(primary_key).reset_index(drop=True).fillna("na")

    return shared_old_df_values, shared_new_df_values


def check_datatypes(old_df, new_df, primary_key, column_subset=None):
    """
    Returns a report summarizing any columns with different datatypes
    NOTE: This function only checks the datatypes of the full column not the individual records
        e.g. a column with mixed types 1, 3, "cat", 4 would be stored as an "object" datatype 
        which would evaluate as equal when compared with another column containing ["dog", 1, 4, "parrot"]

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        column_subset (list of strings): Default value is None which includes all columns.
            The subset of columns under consideration for the comparison 

    Returns:
        report (dict): Summary report showing any columns with different datatypes
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    # Instantiate the report
    report = collections.defaultdict(dict)

    combined_df = pd.concat(
        [old_df.dtypes, new_df.dtypes], axis=1).reset_index()
    combined_df.columns = ['column_name', 'old_df_dtype', 'new_df_dtype']

    # Remove columns that aren't in both dataframes
    combined_df.dropna(inplace=True)

    if column_subset is not None:
        columns_with_changes = combined_df.loc[
            (combined_df['old_df_dtype'] != combined_df['new_df_dtype']) &
            (combined_df['column_name'].isin([primary_key] + column_subset))].reset_index(drop=True)

    else:
        columns_with_changes = combined_df.loc[combined_df['old_df_dtype']
                                               != combined_df['new_df_dtype']].reset_index(drop=True)

    if len(columns_with_changes) == 0:
        report['datatype_changes']['is_equal'] = True

    else:
        report['datatype_changes']['is_equal'] = False
        report['datatype_changes']['summary'] = []
        report['datatype_changes']['values'] = {}

        report['datatype_changes']['summary'].append('{:,} column(s) have different types ({:.1%} of shared columns)'.format(
            len(columns_with_changes), len(columns_with_changes) / len(combined_df)))
        report['datatype_changes']['summary_table'] = columns_with_changes
        report['datatype_changes']['values']['changed_columns'] = list(
            columns_with_changes['column_name'])

    return report


def check_chg_in_values(old_df, new_df, primary_key, column_subset=None):
    """
    Returns a report summarizing any records with changes in values 

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        primary_key (string): The primary key for each dataframe (must be the same primary key)
        column_subset (list of strings): Default value is None which includes all columns.
            The subset of columns under consideration for the comparison 

    Returns:
        report (dict): Summary report showing any records or columns that are shared between dataframes 
            with different values
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    # Instantiate the report
    report = collections.defaultdict(dict)

    # Get records and columns that are shared by both tables
    shared_old_df_values, shared_new_df_values = get_records_in_both_tables(
        old_df, new_df, primary_key, column_subset)

    records_with_changes = shared_new_df_values[primary_key].loc[np.sum(
        shared_old_df_values != shared_new_df_values, axis=1) > 0]

    if len(records_with_changes) == 0:
        report['record_value_changes']['is_equal'] = True

    else:
        report['record_value_changes']['is_equal'] = False
        report['record_value_changes']['summary'] = []
        report['record_value_changes']['values'] = {}

        prop_of_record_changes_by_col = (np.sum(shared_old_df_values != shared_new_df_values, axis=0) /
                                         len(shared_new_df_values)).reset_index()

        prop_of_record_changes_by_col.rename(columns={"index": "column_names",
                                                      0: "changed_records_%"}, inplace=True)

        prop_of_record_changes_by_col.sort_values(
            ['changed_records_%', 'column_names'], ascending=[False, True], inplace=True)

        prop_of_record_changes_by_col.reset_index(drop=True, inplace=True)

        prop_of_record_changes_by_col = prop_of_record_changes_by_col.loc[
            prop_of_record_changes_by_col['changed_records_%'] > 0]

        prop_of_record_changes_by_col['changed_records_%'] = prop_of_record_changes_by_col['changed_records_%'] * 100

        report['record_value_changes']['summary'].append(
            '{:,} records have changed ({:.1%} of shared records)'.format(
                len(records_with_changes), len(records_with_changes) / len(shared_new_df_values)))
        report['record_value_changes']['summary_table'] = prop_of_record_changes_by_col
        report['record_value_changes']['values']['changed_records'] = list(
            records_with_changes.values)
        report['record_value_changes']['values']['changed_columns'] = list(
            prop_of_record_changes_by_col['column_names'])

    return report


def get_record_changes_comparison_df(old_df, new_df, primary_key, column_subset=None):
    """
    Returns a dataframe comparing any records with changes in values by column 

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        primary_key (string): The primary key for each dataframe (must be the same primary key)
        column_subset (list of strings): Default value is None which includes all columns.
            The subset of columns under consideration for the comparison 

    Returns:
        record_changes_comparison_df (pandas dataframe): Summary dataframe showing comparison between
         new and old columns for any records that are shared between dataframes with different values 
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()
    changes_report = check_chg_in_values(
        old_df, new_df, primary_key, column_subset)

    old_df.columns = [col + "_OLD" if col !=
                      primary_key else col for col in old_df.columns]
    new_df.columns = [col + "_NEW" if col !=
                      primary_key else col for col in new_df.columns]

    if changes_report['record_value_changes']['is_equal']:
        return None

    else:
        record_changes_comparison_df = pd.merge(
            old_df.loc[old_df[primary_key].isin(
                changes_report['record_value_changes']['values']['changed_records'])],
            new_df.loc[new_df[primary_key].isin(
                changes_report['record_value_changes']['values']['changed_records'])],
            how='inner', on=primary_key)

        record_changes_comparison_df.set_index(primary_key, inplace=True)

        record_changes_comparison_df = record_changes_comparison_df.reindex(
            sorted(record_changes_comparison_df.columns), axis=1)

        record_changes_comparison_df.reset_index(inplace=True)

        if column_subset is not None:
            record_changes_comparison_df = record_changes_comparison_df[
                [primary_key] + [col_name for col_name in record_changes_comparison_df.columns if any(
                    key_col_name+"_" in col_name for key_col_name in column_subset)]]

        return record_changes_comparison_df


def create_consolidated_report(old_df, new_df, primary_key, column_subset=None):
    """
    Returns a consolidated report with the key changes between two dataframes by test type

    Parameters:
        old_df (pandas dataframe): The first pandas dataframe to be compared
        new_df (pandas dataframe): The second pandas dataframe to be compared
        primary_key (string): The primary key for each dataframe (must be the same primary key)
        column_subset (list of strings): Default value is None which includes all columns.
            The subset of columns under consideration for the comparison 

    Returns:
        consolidated_report (dict): Main report consolidating all other reports which summarizes changes between two dataframes
        record_changes_comparison_df (pandas dataframe): Summary dataframe showing comparison between
            new and old columns for any records that are shared between dataframes with different values 
    """

    # Save copy of dataframes to avoid modifying the original dataframes
    old_df, new_df = old_df.copy(), new_df.copy()

    # Instantiate the report
    base_report = collections.defaultdict(dict)

    # Add meta information to report
    base_report['meta']['title_text'] = 'DataDelta: Dataset Comparison Report'
    base_report['meta']['report_date'] = datetime.today().strftime(
        '%d-%B-%Y (%I:%M %p)')
    base_report['meta']['column_subset'] = column_subset
    base_report['meta']['is_all_equal'] = old_df.equals(new_df)

    # Get summary dataframe reports
    base_report['old_df_table_summary'] = get_df_summary(
        old_df, primary_key, column_subset, 100)
    base_report['new_df_table_summary'] = get_df_summary(
        new_df, primary_key, column_subset, 100)

    column_names_report = check_column_names(old_df, new_df)
    record_count_report = check_record_count(old_df, new_df, primary_key)
    datatypes_report = check_datatypes(
        old_df, new_df, primary_key, column_subset)

    chg_in_values_report = check_chg_in_values(
        old_df, new_df, primary_key, column_subset)

    record_changes_comparison_df = get_record_changes_comparison_df(
        old_df, new_df, primary_key, column_subset)

    # Combine different reports to consolidated report
    consolidated_report = {**base_report,
                           **column_names_report, **record_count_report,
                           **datatypes_report, **chg_in_values_report}

    return consolidated_report, record_changes_comparison_df


def export_html_report(consolidated_report, record_changes_comparison_df,
                       export_file_name='datadelta_html_report.html',
                       overwrite_existing_file=False):
    """
    Exports an html report of the differences between two dataframes

    Parameters:
        consolidated_report (dict): Main report consolidating all other reports which summarizes changes 
            between two dataframes
        record_changes_comparison_df (pandas dataframe): Summary dataframe showing comparison between
            new and old columns for any records that are shared between dataframes with different values
        export_file_name (string): The file name of the report (saved as an .html)
        overwrite_existing_file (boolean): Overwrites the existing file in the directory with the same file name

    Returns:
        Boolean: Saves an html file to current working directory with the summary report and returns True, 
            returns False when file exists in directory and overwrite existing is False 
    """
    max_detail_values = 20

    header_lookup_table = {"added_columns": "Sample Added Columns",
                           "removed_columns": "Sample Removed Columns",
                           "changed_columns": "Sample Changed Columns",
                           "added_records": "Sample Added Records",
                           "removed_records": "Sample Removed Records",
                           "changed_records": "Sample Changed Records"}

    html_template = Template('''
        <html>
            <head>
                <!-- Required meta tags -->
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

                <!-- Bootstrap CSS -->
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

                <!-- Optional JavaScript -->
                <!-- jQuery first, then Popper.js, then Bootstrap JS -->
                <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

                <!-- Custom CSS -->
                <link href="./data/style.css" rel="stylesheet" type="text/css"/>
                <link href='http://fonts.googleapis.com/css?family=Roboto|Lato|Lora' rel='stylesheet' type='text/css'>
            </head>
            <body>
                <h1 class="mainTitle">{{consolidated_report['meta']['title_text']}}</h1>
                <span class="descriptionText"> Summary comparison of changes between two tables </span>
                {% if consolidated_report['meta']['column_subset'] is not none %}
                    <span class="descriptionText"> Subset of Columns Selected: {{consolidated_report['meta']['column_subset']}} </span>
                {% endif %}
                <span class="reportDate">{{consolidated_report['meta']['report_date']}}</span>

                <div class='DataFrameSummaryContainer'>
                    <div id='oldDataFrameSummaryContainer'>
                        <h3 class="text-center sectionTitle">Old Dataframe Summary</h3>
                        <span class="center dataFrameText">Number of Records: {{consolidated_report['old_df_table_summary']['number_of_records']}} | 
                            Number of Columns: {{consolidated_report['old_df_table_summary']['number_of_columns']}}</span>
                        <span class="center dataFrameText">Primary Key: {{consolidated_report['old_df_table_summary']['primary_key']}} | 
                            Primary Key Is Unique: {{consolidated_report['old_df_table_summary']['is_primary_key_unique']}}</span>
                        <div class="summaryDataframeTable">
                        {{consolidated_report['old_df_table_summary']['summary_table'].to_html(
                            classes="table table-striped table-bordered table-hover text-center")}}
                        </div>
                    </div>

                    <div id='newDataFrameSummaryContainer'>
                        <h3 class="text-center sectionTitle">New Dataframe Summary</h3>
                        <span class="center dataFrameText">Number of Records: {{consolidated_report['new_df_table_summary']['number_of_records']}} | 
                            Number of Columns: {{consolidated_report['new_df_table_summary']['number_of_columns']}}</span>
                        <span class="center dataFrameText">Primary Key: {{consolidated_report['new_df_table_summary']['primary_key']}} | 
                            Primary Key Is Unique: {{consolidated_report['new_df_table_summary']['is_primary_key_unique']}}</span>
                        <div class="summaryDataframeTable">
                        {{consolidated_report['new_df_table_summary']['summary_table'].to_html(
                            classes="table table-striped table-bordered table-hover text-center")}}
                        </div>
                    </div>                
                </div>

                <div class="tableChangesContainer">
                    <div class="columnChanges">
                        <h3 class="text-center sectionTitle">Column Changes</h3>
                        {% if consolidated_report['column_name_changes']['is_equal'] %}
                            <div class="text-center contentFormat">
                                The columns are equal
                            </div>
                        
                        {% else %}
                            <ul class="list-group contentFormat">
                                {% for bullet in consolidated_report['column_name_changes']['summary'] %}
                                    <li class="list-group-item">{{ bullet }}</li>
                                {% endfor %}
                            </ul>
                            <br>

                            {% for field_name, values in consolidated_report['column_name_changes']['values'].items() %}
                                <h4 class="text-center detailTitle"> {{ header_lookup_table[field_name] }} </h4>
                                <div class="alert alert-secondary contentFormat"> {{ values[:max_detail_values] }} </div>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="recordCountChanges"> 
                        <h3 class="text-center sectionTitle">Record Count Changes</h3>
                        {% if consolidated_report['record_count_changes']['is_equal'] %}
                            <div class="text-center contentFormat">
                                The number of records is equal
                            </div>
                        
                        {% else %}
                            <ul class="list-group contentFormat">
                                {% for bullet in consolidated_report['record_count_changes']['summary'] %}
                                    <li class="list-group-item">{{ bullet }}</li>
                                {% endfor %}
                            </ul>
                            <br>

                            {% for field_name, values in consolidated_report['record_count_changes']['values'].items() %}
                                <h4 class="text-center detailTitle"> {{header_lookup_table[field_name]}} </h4>
                                <div class="alert alert-secondary contentFormat"> {{ values[:max_detail_values] }} </div>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="dataTypeChanges">
                        <h3 class="text-center sectionTitle">Datatype Changes</h3>
                        {% if consolidated_report['datatype_changes']['is_equal'] %}
                            <div class="text-center contentFormat">
                                The datatypes are equal
                            </div>
                        
                        {% else %}
                            <ul class="list-group contentFormat">
                                {% for bullet in consolidated_report['datatype_changes']['summary'] %}
                                    <li class="list-group-item">{{ bullet }}</li>
                                {% endfor %}
                            </ul>
                            <br>

                            <div class="contentFormat">
                                <h4 class="text-center detailTitle">Summary of Datatype Changes</h4>
                                {{consolidated_report['datatype_changes']['summary_table'].to_html(index=False,
                                        classes="table table-striped table-bordered table-hover text-center")}}
                            </div>
                            

                            {% for field_name, values in consolidated_report['datatype_changes']['values'].items() %}
                                <h4 class="text-center detailTitle"> {{header_lookup_table[field_name]}} </h4>
                                <div class="alert alert-secondary"> {{ values[:max_detail_values] }} </div>
                            {% endfor %}
                        {% endif %}
                    </div>
                </div>

                <div class="recordValueChangesContainer">
                    <div class="recordValueChanges">
                        <h3 class="text-center sectionTitle">Record Value Changes</h3>
                        {% if consolidated_report['record_value_changes']['is_equal'] %}
                            <div class="text-center contentFormat">
                                There are no record changes
                            </div>
                        
                        {% else %}
                            <ul class="list-group contentFormat">
                                {% for bullet in consolidated_report['record_value_changes']['summary'] %}
                                    <li class="list-group-item">{{ bullet }}</li>
                                {% endfor %}
                            </ul>
                            <br>

                            {% if consolidated_report['record_value_changes']['summary_table'] is not none %}
                                <h4 class="text-center detailTitle">Proportion of Records that have Changed for Each Column </h4>
                                <div class="contentFormat">
                                    {{consolidated_report['record_value_changes']['summary_table'][:25].to_html(
                                        classes="table table-striped table-bordered table-hover text-center")}}
                                </div>
                            {% endif %}

                            {% for field_name, values in consolidated_report['record_value_changes']['values'].items() %}
                                <h4 class="text-center detailTitle"> {{header_lookup_table[field_name]}} </h4>
                                <div class="alert alert-secondary contentFormat"> {{ values[:max_detail_values] }} </div>
                            {% endfor %}
                        {% endif %}
                    </div>
                    <div class="recordValueChangesTableContainer">
                        <h3 class="text-center sectionTitle">Comparison of Changed Records</h3>
                        {% if record_changes_comparison_df is none %}
                            <div class="text-center contentFormat">
                                There are no record changes
                            </div>
                        {% else %}
                            <div class="changedRecordsDataframe">
                                {{record_changes_comparison_df[:50].to_html(
                                    classes="table table-striped table-bordered table-hover text-center")}}
                            </div>
                        {% endif %}
                    </div>
                </div>

            </body>
        </html>
        ''')

    with open(export_file_name, 'w') as f:
        if ".html" not in export_file_name:
            export_file_name = export_file_name + ".html"

        if os.path.isfile(export_file_name) & (overwrite_existing_file is False):
            print("File already exists in current directory")
            return False

        else:
            f.write(html_template.render(
                consolidated_report=consolidated_report,
                record_changes_comparison_df=record_changes_comparison_df,
                header_lookup_table=header_lookup_table,
                max_detail_values=max_detail_values))

            print("{} saved successfully.".format(export_file_name))

            return True


def save_pickle(input_dict, export_file_name, overwrite_existing_file=False):
    """
    Saves dictionary to local pickle file

    Parameters:
        input_dict (dict): The dict to be saved - designed for the consolidated report dict
        export_file_name (string): The file name of the report (saved as a .pickle)
        overwrite_existing_file (boolean): Overwrites the existing file in the directory with the same file name

    Returns:
        Boolean: Saves a pickle file to current working directory with the contents of the input dictionary
         and returns True, returns False when file exists in directory and overwrite existing is False 
    """
    if ".pickle" not in export_file_name:
        export_file_name = export_file_name.split(".", 1)[0] + ".pickle"

    if os.path.isfile(export_file_name) & (overwrite_existing_file is False):
        print("File already exists in current directory")
        return False

    with open(export_file_name, 'wb') as file:
        file.write(pickle.dumps(input_dict))

    print("{} saved successfully.".format(export_file_name))


def load_pickle(import_file_name):
    """
    Loads pickle file to object

    Parameters:
        import_file_name (string): The file name of the report (saved as a .pickle)

    Returns:
        loaded_dict: Loaded pickle file - designed for consolidated report dictionary 
    """
    with open(import_file_name, "rb") as input_file:
        loaded_dict = pickle.load(input_file)

    return loaded_dict


if __name__ == '__main__':
    old_df = pd.read_csv('data/MainTestData_old_df.csv')
    new_df = pd.read_csv('data/MainTestData_new_df.csv')
    primary_key = 'A'
    column_subset = None
    consolidated_report, record_changes_comparison_df = create_consolidated_report(
        old_df, new_df, primary_key, column_subset)
    save_pickle(consolidated_report, 'data/correct_column_subset_report.pickle',
                overwrite_existing_file=False)
    export_html_report(consolidated_report, record_changes_comparison_df,
                       export_file_name='datadelta_html_report.html',
                       overwrite_existing_file=True)

# %%
