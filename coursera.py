import requests
import random
import argparse

from lxml import etree
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook


def parse_arguments():
    parser = argparse.ArgumentParser(description="Coursera courses to xlsx.")
    parser.add_argument("xlsx_path", help="path to xlsx file for"
                                          " writing courses info")
    args = parser.parse_args()
    return args


def fetch_page(url, headers):
    page = requests.get(url, headers)
    return page.content


def generate_rand_sequence(diapason, numbers_amount):
    random_list = random.sample(diapason, numbers_amount)
    return random_list


def get_course_url_iter(courses_number=20):
    coursera_feed_url = "https://www.coursera.org/sitemap~www~courses.xml"
    coursera_feed = fetch_page(coursera_feed_url, headers={})
    tree = etree.XML(coursera_feed)
    xml_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ns = {'ns': xml_namespace}
    courses_url_list = tree.findall(".//ns:loc", namespaces=ns)
    all_course_number = len(courses_url_list)
    random_list = generate_rand_sequence(range(all_course_number), courses_number)
    for course_numb in random_list:
        yield courses_url_list[course_numb].text


def pretify_date(raw_date_string):
    date_string = raw_date_string.split(None, maxsplit=1)[1]
    return date_string.capitalize()


def pretify_info(course_info):
    course = course_info.copy()
    course['weeks'] = course['weeks'] if course['weeks'] else "No info"
    course['mark'] = course['mark'].text if course['mark'] else "No info"
    course['date'] = pretify_date(course['date'])
    return course


def get_course_info(course_page):
    page_soup = BeautifulSoup(course_page, 'lxml')

    course_name = page_soup.find('h1', "title display-3-text").text

    course_lang = page_soup.find('div', "language-info").contents[1]

    date_class = "startdate rc-StartDateString caption-text"
    course_date = page_soup.find('div', date_class).find('span').text

    course_weeks_number = len(page_soup.findAll('div', "week"))

    course_mark = page_soup.find('div', "ratings-text bt3-visible-xs")

    course_info= {
        'name': course_name,
        'lang': course_lang,
        'date': course_date,
        'weeks': course_weeks_number,
        'mark': course_mark
    }
    return pretify_info(course_info)


def output_courses_info_to_xlsx(filepath, courses_base):
    headers = ("Course name", "Language", "Start date",
               "Weeks", "Average mark")
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Coursera courses"
    sheet.append(headers)
    for course in courses_base:
        sheet.append((course['name'], course['lang'], course['date'],
                     course['weeks'], course['mark']))
    wb.save(filepath)

if __name__ == '__main__':
    headers = {'accept-language': "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"}
    arguments = parse_arguments()
    xlsx_path = arguments.xlsx_path
    courses_base = []
    try:
        for course_url in get_course_url_iter():
            course_page = fetch_page(course_url, headers=headers)
            course_info = get_course_info(course_page)
            courses_base.append(course_info)
        output_courses_info_to_xlsx(xlsx_path, courses_base)
    except (ValueError, FileNotFoundError) as error:
        print("Something went wrong!", error)
        exit("Exiting...")
