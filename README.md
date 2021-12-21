<div id="top"></div>

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL 3.0 License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/gibbsbravo/DataDelta">
    <img src="images/DataDeltaLogo.png" alt="Logo" width="200" height="200">
  </a>

<h3 align="center">DataDelta</h3>

  <p align="center">
    The best Python package for comparing two dataframes
    <br />
    <a href="https://github.com/gibbsbravo/DataDelta"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/gibbsbravo/DataDelta/issues">Report Bug</a>
    ·
    <a href="https://github.com/gibbsbravo/DataDelta/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

DataDelta is a very useful Python package for easily comparing two pandas dataframes for use in data analysis, data engineering, and tracking table changes across time.

DataDelta generates a <a href="## Example HTML Report Output">report</a> as both a Python dict and HTML file that summarizes the key changes between two dataframes through completing a series of tests (that can also be selected individually). The Python report is intended for use as part of a DevOps / DataOps pipeline for testing to ensure table changes are expected.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

DataDelta is easy to install through pip or feel free to clone locally to make changes.

### Dependencies

DataDelta has very few dependencies:

- <a href='https://pandas.pydata.org/'>pandas</a>: _a fast, powerful, flexible and easy to use open source data analysis and manipulation tool_ - DataDelta is built on for comparing dataframes
- <a href='https://numpy.org/'>numpy</a>: _The fundamental package for scientific computing with Python_ - used for transformations and calculations
- <a href='https://jinja.palletsprojects.com/en/3.0.x/'>jinja2</a>: _a fast, expressive, extensible templating engine_ - used to generate the HTML report
- <a href='https://docs.pytest.org/en/6.2.x/'>pytest</a> (optional): _a mature full-featured Python testing tool that helps you write better programs_ - used for testing

### Installation

- Install using Pip through PyPI:
  ```sh
  pip install datadelta
  ```

OR

- Clone the repo locally:
  ```sh
  git clone https://github.com/gibbsbravo/DataDelta.git
  ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage Examples

- Quick starter code to get summary dataframe changes report:

  ```sh
  import pandas as pd
  import datadelta as delta

  old_df = pd.read_csv('MainTestData_old_df.csv') # Add your old dataframe here
  new_df = pd.read_csv('MainTestData_new_df.csv') # Add your new dataframe here
  primary_key = 'A' # Set the primary key
  column_subset = None # Specify the subset of columns of interest or leave None to compare all columns

  # The consolidated_report dictionary will contain the summary changes
  consolidated_report, record_changes_comparison_df = delta.create_consolidated_report(
      old_df, new_df, primary_key, column_subset)

  # This will create a report named datadelta_html_report.html in the current working directory containing the summary changes
  delta.export_html_report(consolidated_report, record_changes_comparison_df,
                        export_file_name='datadelta_html_report.html',
                        overwrite_existing_file=False)
  ```

- Get dataframe summary:

  ```sh
    import pandas as pd
    import datadelta as delta

    new_df = pd.read_csv('MainTestData_new_df.csv') # Add your new dataframe here

    # Returns a report summarizing the key attributes and values of a dataframe
    summary_report = delta.get_df_summary(
      input_df=new_df, primary_key=primary_key, column_subset=column_subset, max_cols=15)
  ```

- Get record count changes report:

  ```sh
    old_df = pd.read_csv('MainTestData_old_df.csv') # Add your old dataframe here
    new_df = pd.read_csv('MainTestData_new_df.csv') # Add your new dataframe here
    primary_key = 'A' # Set the primary key
    column_subset = None # Specify the subset of columns of interest or leave None to compare all columns

    # Returns a report summarizing any changes to the number of records (and composition) between two dataframes
    record_count_change_report = delta.check_record_count(
      old_df, new_df, primary_key)
  ```

Other functions include:

- check_column_names: Returns a report summarizing any changes to column names between two dataframes
- check_datatypes: Returns a report summarizing any columns with different datatypes
- check_chg_in_values: Returns a report summarizing any records with changes in values
- get_records_in_both_tables: Returns the records found in both dataframes
- get_record_changes_comparison_df: Returns a dataframe comparing any records with changes in values by column
- export_html_report: Exports an html report of the differences between two dataframes

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Example Report -->

## Example HTML Report Output

![Report Screenshot1][report-screenshot1]
![Report Screenshot2][report-screenshot2]
![Report Screenshot3][report-screenshot3]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the GNU General Public License v3 (GPLV3) License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Andrew Gibbs-Bravo - andrewgbravo@gmail.com

Project Link: [https://github.com/gibbsbravo/DataDelta](https://github.com/gibbsbravo/DataDelta)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/gibbsbravo/DataDelta.svg?style=for-the-badge
[contributors-url]: https://github.com/gibbsbravo/DataDelta/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/gibbsbravo/DataDelta.svg?style=for-the-badge
[forks-url]: https://github.com/gibbsbravo/DataDelta/network/members
[stars-shield]: https://img.shields.io/github/stars/gibbsbravo/DataDelta.svg?style=for-the-badge
[stars-url]: https://github.com/gibbsbravo/DataDelta/stargazers
[issues-shield]: https://img.shields.io/github/issues/gibbsbravo/DataDelta.svg?style=for-the-badge
[issues-url]: https://github.com/gibbsbravo/DataDelta/issues
[license-shield]: https://img.shields.io/github/license/gibbsbravo/DataDelta.svg?style=for-the-badge
[license-url]: https://github.com/gibbsbravo/DataDelta/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[report-screenshot1]: images/DatasetComparisonReport1.png
[report-screenshot2]: images/DatasetComparisonReport2.png
[report-screenshot3]: images/DatasetComparisonReport3.png
