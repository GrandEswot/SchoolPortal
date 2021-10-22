import json
import os
import requests
import time


persons_ids = {}


def prepare(func):
    def wrapped(person, date):
        global persons_ids
        if person == 'stepan':

            access_token = os.getenv("SPTOKEN")
        else:
            access_token = "27YtgVjGSibtpF4yP2RdgtF0piUrhWeW"

        school_id = 54903

        if persons_ids.setdefault(person) is None:
            person_id = get_person_id(access_token)
            persons_ids[person] = person_id
            print(persons_ids)
        else:
            person_id = persons_ids.get(person)
        result = func(person, date=date, access_token=access_token, person_id=person_id, school_id=school_id)
        return result
    return wrapped


def get_person_id(access_token):


    url = 'https://api.school.mosreg.ru/v2.0/users/me'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }
    s = requests.get(url=url, headers=headers)
    person_id = json.loads(s.text).get('personId')
    print(person_id)
    return person_id


@prepare
def get_homework(person, date, access_token, person_id, school_id):

    print(date)
    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/school/{school_id}/homeworks?startDate={date}&endDate={date}'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    homework = ''
    subject_name = ''

    s = requests.get(url=url, headers=headers)
    while len(homework) == 0:
        if len(homework) > 0:
            break
        try:
            homeworks = json.loads(s.text).get('works')
            subjects = json.loads(s.text).get('subjects')
            if len(homeworks) == 0:
                return 'Неправильно выбрана дата. ДЗ не найдено'
            for task in homeworks:
                subject_id = task.get('subjectId')
                for subject in subjects:
                    if subject_id == subject['id']:
                        subject_name = subject['name']
                homework += f"\n{subject_name}: \n\t{task.get('text')}\n"
                homework += '========================='
        except Exception:
            print('API не отработало')
            homework = 'Произошла ошибка на сервере. Давай еще раз!'
    return homework


def get_marks(person_id, access_token, subject_id):
    marks = []
    edu_year = 0
    t = time.gmtime()
    date_now = f"{t[0]}-{t[1]}-{t[2]}"
    if 9 <= time.gmtime()[1] <= 12:
        edu_year = time.gmtime()[0]
    elif 1 <= time.gmtime()[1] <= 5:
        edu_year = time.gmtime()[0] - 1

    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/subjects/{subject_id}/marks/{edu_year}-09-01/{date_now}'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    s = requests.get(url=url, headers=headers)
    marks_array = json.loads(s.text)
    for mark in marks_array:
        marks.append(int(mark.get('value')))
    return marks


def get_subjects(person_id, access_token):

    subjects = dict()

    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/edu-groups'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    s = requests.get(url=url, headers=headers)
    edu_groups = json.loads(s.text)[2].get('subjects')
    for subject in edu_groups:
        subjects[subject.get('id')] = subject.get('name')

    return subjects


@prepare
def get_marks_per_subject(person, date, access_token, person_id, school_id):
    statistic_data = dict()
    result = ''
    subjects: dict = get_subjects(person_id, access_token)

    for subject_id, subject_name in subjects.items():
        statistic_data[subject_name] = get_marks(person_id, access_token, subject_id)

    for subject_name, marks in statistic_data.items():
        try:
            result += f'\n{subject_name}: средний бал - {round((sum(marks) / len(marks)), 1)}\n'
        except ZeroDivisionError:
            result += f'\n{subject_name}: оценок нет!\n'
    return result


def get_edugroup(person_id, access_token):
    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/edu-groups'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    s = requests.get(url=url, headers=headers)
    edu_group = json.loads(s.text)[2].get('id_str')
    return edu_group


@prepare
def get_shedules(person, date, access_token, person_id, school_id):
    lessons = []
    schedule = ''
    group_id = get_edugroup(person_id, access_token)
    t = time.gmtime()
    date = f"{t[0]}-{t[1]}-{t[2] + 1}"
    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/groups/{group_id}/schedules?startDate={date}&endDate={date}'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    s = requests.get(url=url, headers=headers)
    schedules = json.loads(s.text).get('days')[0].get('lessons')
    subjects = get_subjects(person_id, access_token)
    for lesson in schedules:
        lessons.append(lesson.get('subjectId'))
    for index, lesson_id in enumerate(lessons):
        schedule += f'\n{index + 1} - {subjects.get(lesson_id)}'

    return schedule


# print(get_shedules('sergey', '1'))
