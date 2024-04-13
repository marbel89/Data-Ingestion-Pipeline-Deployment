import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

""" Placeholder for docstring """


def clean_students_table(df):

    """
    Clean students table: Explode contact_info, replaces null values, changes dtypes to float for now

    Returns cleaned student df as well as missing entries (no courses taken, no job id)
    """

    temp = df["contact_info"].copy()
    # Better than plain eval:
    temp = temp.apply(ast.literal_eval)
    data = {}

    # Iterate over each dictionary item in contact_info and explode
    for dictionary in temp:
        for key, value in dictionary.items():
            if key in data:
                data[key].append(value)
            else:
                data[key] = [value]

    # Merge articulated contact info and drop old contact info column
    new = pd.DataFrame(data)
    merge = pd.concat([df, new], axis=1)
    merge = merge.drop("contact_info", axis=1)

    # Splitting contact info into separate fields
    splitting = merge.mailing_address.str.split(",", expand=True)
    splitting.columns = ["street", "city", "state", "zip_code"]
    merge = pd.concat([merge.drop("mailing_address", axis=1), splitting], axis=1)

    """ Fix data types """

    # Replace "None" values in path id and time spent with proper 0s
    df['current_career_path_id'] = np.where(df['current_career_path_id'].isnull(), 0, df['current_career_path_id'])
    df["time_spent_hrs"] = np.where(df["time_spent_hrs"].isnull(), 0, df["time_spent_hrs"])
    df.job_id = df.job_id.astype(float)
    df.current_career_path_id = df.current_career_path_id.astype(float)
    df.num_course_taken = df.num_course_taken.astype(float)
    df.time_spent_hrs = df.time_spent_hrs.astype(float)

    """ Separate missing data """

    missing_data = pd.DataFrame()
    students_missing_courses = df[df["num_course_taken"].isnull()]
    missing_data = pd.concat([missing_data, students_missing_courses])
    df = df.dropna(subset=["num_course_taken"])

    missing_job_id = df[df["job_id"].isnull()]
    missing_data = pd.concat([missing_data, missing_job_id])
    df = df.dropna(subset=["job_id"])

    return df, missing_data





def clean_courses_table(df):
    pass


def clean_student_jobs(df):
    pass


if __name__ == '__main__':
    print('PyCharm')
