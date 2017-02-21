Coursera Dump
===================

The script coursera.py pulls out Coursera courses urls from Coursera [xml-feed](https://www.coursera.org/sitemap~www~courses.xml). 

The script takes the path to xlsx file as required console parameter.

Then it collects the information about each course using course's url. 

Finally, the script writes all obtained information about course into xlsx-file. 

How to run
---------- 

Clone this repository. Then go to the repository directory.

Install all requirements:
```
pip3 install -r requirements.txt
```
Run the script:
```
python3 coursera.py [-h] xlsx_path
```

Usage
-----

```
~$ python3 coursera.py ~/coursera.xlsx

```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
