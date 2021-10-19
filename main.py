import json
import os
import requests
import time


persons_ids = {}


def get_person_id(access_token):
    # access_token = "KHL3Y4DQ8DyqDix1atnnQTAGzqChdAG1"

    url = 'https://api.school.mosreg.ru/v2.0/users/1000006512438'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }
    s = requests.get(url=url, headers=headers)
    person_id = json.loads(s.text).get('personId')
    print(person_id)
    return person_id


def get_homework(date, access_token, person_id, school_id):

    print(date)
    url = f'https://api.school.mosreg.ru/v2.0/persons/{person_id}/school/{school_id}/homeworks?startDate={date}&endDate={date}'
    headers = {
        "accept": "application/json",
        'Access-Token': access_token,
    }

    homework = ''
    subject_name = ''
    result = ''

    s = requests.get(url=url, headers=headers)
    while len(homework) == 0:
        if len(homework) > 0:
            break
        try:
            homeworks = json.loads(s.text).get('works')
            subjects = json.loads(s.text).get('subjects')

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


def main(person, date):
    global persons_ids
    if person == 'Stepan':
        access_token = "KHL3Y4DQ8DyqDix1atnnQTAGzqChdAG1"
        # access_token = os.getenv("SPTOKEN")
    else:
        access_token = 'SergeyToken'

    school_id = 54903

    if persons_ids.setdefault(person) is None:
        person_id = get_person_id(access_token)
        persons_ids[person] = person_id
        print(persons_ids)
    else:
        person_id = persons_ids.get(person)
    result = get_homework(date, access_token=access_token, person_id=person_id, school_id=school_id)
    return result
