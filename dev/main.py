import sqlite3
import pandas as pd
import numpy as np
import ast
import logging
from datetime import datetime
import os

""" Placeholder for docstring """

logging_level = logging.DEBUG

logging.basicConfig(filename="./dev/clean_db.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filemode="w", level=logging_level, force=True)
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.debug(os.getcwd())


def clean_students_table(df):
    """
    Clean students table: Explode contact_info, replaces null values, changes dtypes to float for now

    Returns cleaned student df as well as missing entries (no courses taken, no job id)
    """

    # Necessary preparation of contact info field before exploding
    temp = df["contact_info"].copy()
    # Better than plain eval:
    temp = temp.apply(ast.literal_eval)
    data = {}

    # logger.debug(f"Before iteration {temp.head()}")

    # Iterate over each dictionary item in contact_info and explode
    for dictionary in temp:
        for key, value in dictionary.items():
            if key in data:
                data[key].append(value)
            else:
                data[key] = [value]

    # Merge articulated contact info and drop old contact info column
    new_data = pd.DataFrame(data)

    logger.debug(f"after iteration, new data df {new_data.columns}. Length: {len(new_data)}")
    """ HERE IS THE BORK UP? """
    new_data.to_csv("new_data_sanitycheck.csv")
    merge = pd.concat([df, new_data], axis=1)
    logger.debug(f"merge {merge.columns}. Length: {len(merge)}")
    # logger.debug(merge.columns)
    merge = merge.drop("contact_info", axis=1)
    merge.to_csv("merge_test.csv")
    # logger.debug(f"after first merge {merge.head()}")

    # Splitting contact info into separate fields



    splitting = merge["mailing_address"].str.split(",", expand=True)

    logger.debug(f"splitting 1 {splitting.columns}. Length: {len(splitting)}")
    splitting.columns = ["street", "city", "state", "zip_code"]
    splitting.to_csv("splitting_test.csv")
    # df = pd.concat([merge.drop("mailing_address", axis=1), splitting], axis=1) depreciated
    df = pd.concat([merge.drop("mailing_address", axis=1), splitting], axis=1)

    logger.debug(f"Length df {len(df)}")

    """ Fix data types """

    # Replace "None" values in path id and time spent with proper 0s
    df['current_career_path_id'] = np.where(df['current_career_path_id'].isnull(), 0, df['current_career_path_id'])
    df["time_spent_hrs"] = np.where(df["time_spent_hrs"].isnull(), 0, df["time_spent_hrs"])
    df.job_id = df.job_id.astype(float)
    df.current_career_path_id = df.current_career_path_id.astype(float)
    df.num_course_taken = df.num_course_taken.astype(float)
    df.time_spent_hrs = df.time_spent_hrs.astype(float)

    logger.debug(f"Length df {len(df)}")

    """ Separate missing data """

    missing_data = pd.DataFrame()
    logger.debug(f"Missing data length {len(missing_data)}")

    students_missing_courses = df[df["num_course_taken"].isnull()]
    logger.debug(f"Seperating: len missing courses {len(students_missing_courses)}")

    missing_job_id = df[df["job_id"].isnull()]
    logger.debug(f"Seperating: len missing job ids {len(missing_job_id)}")

    missing_data = pd.concat([students_missing_courses, missing_job_id])
    logger.debug(f"Seperating: len missing data {len(missing_data)}")

    df = df.dropna(subset=["num_course_taken"])
    df = df.dropna(subset=["job_id"])

    """
        missing_data = pd.DataFrame()

        students_missing_courses = df[df["num_course_taken"].isnull()]
        logger.debug(f"Length students missing courses: {len(students_missing_courses)}")

        missing_data = pd.concat([missing_data, students_missing_courses])

        df = df.dropna(subset=["num_course_taken"])

        logger.debug(f"Length of missing data num_course_taken: {len(missing_data)} ")

        missing_job_id = df[df["job_id"].isnull()]
        missing_data = pd.concat([missing_data, missing_job_id])
        df = df.dropna(subset=["job_id"])

        logger.debug(f"Length of missing data + missing job_ids: {len(missing_data)}")


        """

    return df, missing_data




def clean_courses_table(df):
    """
    The only thing we need to do is add the career_path_id 0 to provide for null values

    :param df:
    :return df:
    """

    new_row = pd.DataFrame({"career_path_id": [0], "career_path_name": ["N/A"], "hours_to_complete": 0})
    df = pd.concat([new_row, df], ignore_index=True)
    return df


def clean_student_jobs(df):
    """
    We drop the duplicates.

    :param df:
    :return df:
    """
    return df.drop_duplicates()


def test_null_values(df):
    """
    Tests to check if there are still null values in the data

    :param df:
    :returns none:

    """
    df_0 = df[df.isnull().any(axis=1)]
    num_missing = len(df_0)

    try:
        assert num_missing == 0, "There are " + str(num_missing) + "nulls in the table."
    except AssertionError as ae:
        logger.exception(ae)
        raise ae
    else:
        logger.info("There are no null values.")


def test_schema(local_df, db_table):
    """
    Tests if the dtypes (schema) of the local df are the same as the target database

    :param local_df:
    :param db_table:

    :returns none:

    """
    errors = []
    for column in db_table.columns:
        try:
            if local_df[column].dtype != db_table[column].dtype:
                errors.append(column)
        except Exception as e:
            logger.exception(f"Error comparing column '{column}': {e}")
            raise ValueError(f"Error comparing column '{column}': {e}")
    if errors:
        err_msg = f"The following columns have different dtypes: {', '.join(errors)}"
        logger.error(err_msg)
        raise ValueError(err_msg)
    else:
        logger.info("Dtypes check out.")


def test_num_columns(local_df, db_table):
    """
      Tests if the number of columns in the local DataFrame matches the number of columns in the database table.

      :param local_df: The DataFrame representing the local data.
      :param db_table: The DataFrame representing the database table.

      :raises ValueError: If the number of columns in local_df doesn't match db_table.
    """
    try:
        assert len(local_df.columns) == len(db_table.columns)
    except AssertionError as ae:
        logger.exception("Number of columns mismatch")
        raise ValueError("Number of columns mismatch") from ae
    else:
        logger.info('Number of columns check out.')


def test_path_id(students, careers):
    """
       Tests if all career path IDs present in the students DF are also present in the careers DF.

       :param students: DataFrame representing student data.
       :param careers: DataFrame representing career data.

       :raises ValueError: If any career path IDs are missing in the careers DataFrame.

       """
    student_table = students.current_career_path_id.unique()
    is_subset = np.isin(student_table, careers.career_path_id.unique())
    missing_path_ids = student_table[~is_subset]
    try:
        assert len(missing_path_ids) == 0, f"Career path ID(s) missing: {list(missing_path_ids)} in careers DataFrame"
    except AssertionError as ae:
        logger.exception(ae)
        raise ValueError("Career path ID(s) missing") from ae
    else:
        logger.info("All career_path_ids are present.")


def test_job_id(students, jobs):
    """
          Tests if all Job IDs present in the students DF are also present in the students_jobs DF.

          :param students: DataFrame representing student data.
          :param jobs: DataFrame representing career data.

          :raises ValueError: If any Job IDs are missing in the jobs DataFrame.

          """
    student_table = students.job_id.unique()
    logger.debug(f"Length students table {len(student_table)}")
    is_subset = np.isin(student_table, jobs.job_id.unique())
    logger.debug(f"Length is subset {len(is_subset)}")
    missing_job_ids = student_table[~is_subset]
    logger.debug(f"Length missing job ids {len(missing_job_ids)}, {missing_job_ids}")
    try:
        assert len(missing_job_ids) == 0, f"Job ID(s) missing: {list(missing_job_ids)} in student_jobs DataFrame"
    except AssertionError as ae:
        logger.exception(ae)
        raise ValueError("Job ID(s) missing") from ae
    else:
        logger.info("All job_ids are present.")


def main():
    """
    Version and changelog handling

    """
    logger.info("Job is starting.")
    next_ver = None
    try:
        with open("./dev/changelog.md", "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            next_ver = 1
        else:
            # Extracting version number from the first line in the format x.x.x
            version = lines[0].split(".")[2].strip()
            next_ver = int(version) + 1
            logger.info(f"Next version number: {next_ver}")

        # Append the new version to the changelog
        with open("./dev/changelog.md", "a+") as f:
            f.write(f"\nVersion {next_ver}, {datetime.now().strftime('%Y-%m-%d')}: \n")

        logger.info("Version incremented successfully.")
    except FileNotFoundError:
        logger.error("Changelog file not found!")
    except Exception as e:
        logger.error(f"An unexpected error occurred when editing the changelog: {e}")

    """
    Database connection and queries
    
    """

    db = "./db/data.db"
    try:
        con = sqlite3.connect(db)
        logger.info("Connection successful.")
        logger.info(f"Total changes since last commit: {con.total_changes}")

        cur = con.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        logger.info("Tables in the database:")
        for table in tables:
            logger.info(table[0])

        courses = "SELECT * FROM courses;"
        student_jobs = "SELECT * FROM student_jobs;"
        students = "SELECT * FROM students;"
        df_courses = pd.read_sql(courses, con)
        df_student_jobs = pd.read_sql(student_jobs, con)
        df_students = pd.read_sql(students, con)

        clean_table = pd.DataFrame()
        missing_table = pd.DataFrame()

        # This is borked? ->

        try:
            clean_table = pd.read_sql_query("SELECT * FROM main_cancelled_subscribers", con)
            missing_table = pd.read_sql_query("SELECT * FROM incomplete_data_subscribers", con)
            new_students = df_students[~np.isin(df_students.uuid.unique(), clean_table.uuid.unique())]
            logger.debug(f"Length difference df_students und clean_table {len(new_students)}")
            new_students.to_csv("new_students_sanitycheck.csv")
        except sqlite3.Error as sqe:
            # Log the error and fallback to df_students
            logger.error(f"Database-operation error: {sqe}. Falling back to existing tables.")
            new_students = df_students
            clean_table = []
        except Exception as e:
            # Log the error and fallback to df_students
            logger.error(f"Unexpected error: {e}. Falling back to existing tables.")
            new_students = df_students
            clean_table = []
        finally:
            if con:
                con.close()

        # Actual cleaning of data

        cleaned_new_students, missing_data = clean_students_table(new_students)
        cleaned_new_students.to_csv("cleaned_new_students.sanitycheck.csv")
        missing_data.to_csv("missing_data_sanitycheck.csv")

        # Comparison and filtering
        try:
            new_missing_data = missing_data[~np.isin(missing_data.uuid.unique(), missing_table.uuid.unique())]
        except Exception as e:
            logger.error(f"An unexpected error occurred when comparing missing data: {e}")
            new_missing_data = missing_data

        # Upsertion, if there is new data
        if len(new_missing_data) > 0:
            con = sqlite3.connect(db)
            missing_data.to_sql("incomplete_data_subscribers", con, if_exists="append", index=False)
            con.close()
        if len(cleaned_new_students) > 0:
            # Further processing
            cleaned_career_paths = clean_courses_table(df_courses)
            cleaned_student_jobs = clean_student_jobs(df_student_jobs)

            # Unit Testing
            #test_job_id(cleaned_new_students, cleaned_student_jobs)
            test_path_id(cleaned_new_students, cleaned_career_paths)

            # Merging cleaned data
            obt = cleaned_new_students.merge(cleaned_career_paths, left_on="current_career_path_id",
                                             right_on="career_path_id", how="left")
            obt = obt.merge(cleaned_student_jobs, on="job_id", how="left")

            if len(clean_table) > 0:
                test_num_columns(obt, clean_table)
                test_schema(obt, clean_table)
                test_null_values(obt)

            # Sanity check
            con = sqlite3.connect(db)
            obt.to_sql("main_cancelled_subscribers", con, if_exists="append", index=False)
            clean_table = pd.read_sql_query("SELECT * FROM main_cancelled_subscribers", con)
            con.close()

            # Create .csv output
            clean_table.to_csv("./main_cancelled_subscribers.csv")

            new_lines = [
                "## 0.0" + str(next_ver) + "\n" + "### Added\n" +
                "- " + str(len(obt)) + " more data to database of raw data\n" +
                "- " + str(len(new_missing_data)) + " new missing data to missing_data table\n\n"
            ]

            all_lines = "".join(new_lines + lines)
            logger.debug(all_lines)

            with open("./dev/changelog.md", "w") as f:
                for line in all_lines:
                    f.write(line)
        else:
            logger.info("No new data")

        logger.info("End job")

    except sqlite3.OperationalError as e:
        if "unable to open database file" in str(e):
            error_msg = f"Error connecting: unable to open database file '{db}'."
        elif "permission denied" in str(e):
            error_msg = f"Error connecting: permission denied for database file '{db}'. Check file permissions."
        else:
            error_msg = f"Error connecting: {e}"
        logger.error(error_msg)


if __name__ == '__main__':
    main()
