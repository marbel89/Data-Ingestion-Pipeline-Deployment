# Automated data ingestion pipeline (WIP)

This project consists of an automated pipeline, channeling and wrangling/cleaning data from a SQlite database to be used in analytics.

Included are:
<ul>
  <li>Unit Tests</li>
  <li>Detailed error and debugging logs</li>
  <li>Automatic version checking and updating</li>
  <li>Upserting cleaned data into live database</li>
</ul>

Tools used are
<ul>
  <li>Python</li>
  <li>Jupyter Notebook for initial explorative data analysis</li>
  <li>Bash</li>
  <li>Unit test and Logging libraries</li>
</ul>


## Roadmap

Features to be implemented with next releases:

<ol>
  <li>Bugfixing for Bash script</li>
  <li>Fleshing out readme and writeup</li>
</ol>

Features already implemented:

<ul>
  <li>Notebook EDA and cleansing</li>
  <li>Standalone Python script</li>
  <li>Unit-Testing for data-validity</li>
  <li>Logging</li>
  <li>Bash-Script for automation</li>
</ul>

# Instructions

<ol>
  <li>Run script.sh (in Windows, make sure Python is part of the environmental path variable)</li>
  <li>Follow prompts</li>
  <li>Bash script will start dev/main.py to clean tables from a database (db/data.db)</li>
  <li>Unit-Testing and extensive logging will catch possible errors in detail</li>
  <li>Version updates are automatic after each run that adds new data, and written to dev/changelog.md</li>
  <li>In case of changelog.md updates, the script can copy dev files (database with new entries...) to prod folder (WIP)</li>
</ol>
