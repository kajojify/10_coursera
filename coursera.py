import requests
import random
import os.path as op

from lxml import etree
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook


def get_course_iter(courses_number=20):
    coursera_feed_url = "https://www.coursera.org/sitemap~www~courses.xml"
    xml_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    coursera_feed = requests.get(coursera_feed_url)
    if coursera_feed.status_code != 200:
        raise requests.HTTPError("HTTP request error!")
    tree = etree.XML(coursera_feed.content)
    ns = {'ns': xml_namespace}
    courses_url_list = tree.findall(".//ns:loc", namespaces=ns)
    all_course_number = len(courses_url_list)
    random_list = random.sample(range(all_course_number), courses_number)
    for course_numb in random_list:
        yield courses_url_list[course_numb].text


def get_course_info(course_url):
    headers = {'accept-language': "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"}
    course_page = requests.get(course_url, headers=headers)
    page_soup = BeautifulSoup(course_page.content, 'lxml')

    course_name_elem = page_soup.find('div', "title display-3-text")
    course_name = course_name_elem.text if course_name_elem else None

    course_lang_elem = page_soup.find('div', "language-info")
    course_lang = course_lang_elem.contents[1] if course_lang_elem else None

    date_class = "startdate rc-StartDateString caption-text"
    course_date_elem = page_soup.find('div', date_class).find('span')
    course_date = course_date_elem.text if course_date_elem else None
    course_date = course_date

    week_elems_number = len(page_soup.findAll('div', "week"))
    course_weeks_number = week_elems_number if week_elems_number else None

    mark_div = page_soup.find('div', "ratings-text bt3-visible-xs")
    course_mark = mark_div.text if mark_div else None

    course_info = (course_name, course_lang, course_date,
                   course_weeks_number, course_mark)
    return course_info


def output_courses_info_to_xlsx(filepath, courses_base):
    headers = ("Course name", "Language", "Start date",
               "Weeks", "Average mark")
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Coursera courses"
    sheet.append(headers)
    for course in courses_base:
        sheet.append([course_info if course_info is not None
                      else "No info" for course_info in course])
    wb.save(filepath)

if __name__ == '__main__':
    xlsx_path = input("Enter the path to the xlsx file --- ")
    xlsx_path_ext = op.splitext(xlsx_path)[1]
    xlsx_dir = op.dirname(xlsx_path)
    if not op.isdir(xlsx_dir):
        exit("There is no such directory {}".format(xlsx_dir))
    if xlsx_path_ext != ".xlsx":
        exit("The file extension isn't xlsx!")
    courses_base = []
    try:
        for course_url in get_course_iter():
            course_info = get_course_info(course_url)
            courses_base.append(course_info)
        output_courses_info_to_xlsx(xlsx_path, courses_base)
    except (requests.HTTPError, ValueError) as error:
        print("Something went wrong!", error)
        exit("Exiting...")
