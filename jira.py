import requests
from calendar import monthcalendar
from datetime import datetime

URLS = {
    'log-work': 'https://<jira-host>/rest/tempo-rest/1.0/worklogs/%s'
}

ISSUES = {
    'general-work': 'JIRA-1',
    'absence': 'JIRA-2'
}

TASKS = {
    'daily' : {
        'issue': ISSUES['general-work'],
        'duration': 0.5,
        'comment': 'Daily'
    },
    'planning' : {
        'issue': ISSUES['general-work'],
        'duration': 1,
        'comment': 'Planning'
    },
    'retrospective' : {
        'issue': ISSUES['general-work'],
        'duration': 1,
        'comment': 'Retrospective'
    },
    'absence' : {
        'issue': ISSUES['absence'],
        'duration': 8,
        'comment': 'Day off'
    }
}

class Timesheet:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def log_time(self, issue, date, duration, comment):
        payload = {
            'id': '',
            'type': 'issue',
            'use-ISO8061-week-numbers': 'true',
            'ansidate': date.strftime("%Y-%m-%d") + 'T09:00',
            'ansienddate': datetime.now().strftime("%Y-%m-%d"),
            'selected-panel': '',
            'analytics-origin-page': 'Issue Search or Issue View',
            'analytics-origin-view': 'Tempo Issue Panel',
            'analytics-origin-action': 'Clicked Log Work Button',
            'analytics-page-category': 'JIRA',
            'startTimeEnabled': 'true',
            'actionType': 'logTime',
            'tracker': 'false',
            'preSelectedIssue': issue,
            'planning': 'false',
            'user': self.username,
            'issue': issue,
            'date': date.strftime("%d/%b/%Y"),
            'enddate': datetime.now().strftime("%d/%b/%Y"),
            'worklogtime': '9:00 am',
            'time': duration,
            'remainingEstimate': 0,
            'comment': comment
        }
        return requests.post(URLS['log-work'] % issue, data=payload, auth=(self.username, self.password))

    def log_task(self, task, date):
        return self.log_time(task['issue'], date, task['duration'], task['comment'])

def business_days_in_month(year, month):
    return {day for week in monthcalendar(year, month) for day in week[:5] if day != 0}

def work_days_in_range(work_days, start, end):
    return {day for day in range(start, end+1) if day in work_days}

def work_days_in_ranges(work_days, ranges):
    return reduce(set.union, [work_days_in_range(work_days, start, end) for start, end in ranges], set())

timesheet = Timesheet('Name.Surname', 'password')

year=datetime.now().year
month=datetime.now().month

# Absence
absence_days = set() # ex: {1, 4}
map(lambda day: timesheet.log_task(TASKS['absence'], datetime(year, month, day)), absence_days)

# Work
work_days = business_days_in_month(year, month) - absence_days

#-# Daily
# map(lambda day: timesheet.log_task(TASKS['daily'], datetime(year, month, day)), work_days)

#-# Range
# task_1 = work_days_in_ranges(work_days, [(2,11), (22,31)])
# map(lambda day: timesheet.log_time('JIRA-1', datetime(year, month, day), 7.5, 'Implementation and testing'), task_1)

#-# Individual
# timesheet.log_time('JIRA-2', datetime(year, month, 1), 2.0, 'Fixed some bug.')
# timesheet.log_time('JIRA-3', datetime(year, month, 1), 1.0, 'Helped colleague with issue.')
# timesheet.log_time('JIRA-4', datetime(year, month, 1), 4.5, 'Implemented new feature.')
