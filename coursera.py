import requests
import random

from lxml import etree
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook


def get_course_iter(courses_number=20):
    coursera_feed_url = "https://www.coursera.org/sitemap~www~courses.xml"
    xml_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    coursera_feed = requests.get(coursera_feed_url)
    tree = etree.XML(coursera_feed.content)
    ns = {'ns': xml_namespace}
    courses_url_list = tree.findall(".//ns:loc", namespaces=ns)
    all_course_number = len(courses_url_list)
    random_list = random.sample(range(all_course_number), courses_number)
    for course_numb in random_list:
        yield courses_url_list[course_numb].text


def pretify_date(raw_date_string):
    date_string = raw_date_string.split(None, maxsplit=1)[1]
    return date_string.capitalize()


def get_course_info(course_url):
    headers = {'accept-language': "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"}
    course_page = requests.get(course_url, headers=headers)
    page_soup = BeautifulSoup(course_page.content, 'lxml')

    course_name = page_soup.find('h1', "title display-3-text").text

    course_lang = page_soup.find('div', "language-info").contents[1]

    date_class = "startdate rc-StartDateString caption-text"
    course_date = page_soup.find('div', date_class).find('span').text
    course_date = pretify_date(course_date)

    week_elems_number = len(page_soup.findAll('div', "week"))
    course_weeks_number = week_elems_number if week_elems_number else "No info"

    mark_div = page_soup.find('div', "ratings-text bt3-visible-xs")
    course_mark = mark_div.text if mark_div else "No info"

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
        sheet.append(course)
    wb.save(filepath)

if __name__ == '__main__':
    xlsx_path = input("Enter the path to the xlsx file --- ")
    courses_base = []
    try:
        for course_url in get_course_iter():
            course_info = get_course_info(course_url)
            courses_base.append(course_info)
        output_courses_info_to_xlsx(xlsx_path, courses_base)
    except (ValueError,FileNotFoundError) as error:
        print("Something went wrong!", error)
        exit("Exiting...")
