import os
import json
import requests
import smtplib
import datetime
import time


today = datetime.date.today()
ONE_DAY = 24 * 60 * 60

try:
    script_dir = os.path.dirname(__file__)
    rel_path = "settings.json"
    settings_path = os.path.join(script_dir, rel_path)
    with open(settings_path) as data_file:
        try:
            data = json.load(data_file)
            # this is retrieved from https://www.beeminder.com/settings/advanced_settings
            AUTH_TOKEN = data['beeminder_auth_token']
            GMAIL_USER = data['gmail_email']
            GMAIL_PWD = data['gmail_password']
            EMAIL_RECIPIENTS = data['email_recipients']
        except KeyError as e:
            print 'Make sure that credentials.json is correct. the following key is missing: {}'.format(e)
            quit()
except IOError:
    print 'Couldn\'t find settings.json. Please follow the README'
    quit()


# copied from http://stackoverflow.com/questions/10147455/trying-to-send-email-gmail-as-mail-provider-using-python
def send_email(recipients, subject, body):
    assert isinstance(recipients, list), 'recipients must be a list'

    # Prepare actual message
    message = '\From: {}\nTo: {}\nSubject: {}\n\n{}'.format(
        GMAIL_USER, ", ".join(recipients), subject, body
    )

    try:
        server = smtplib.SMTP("smtp.gmail.com:587") # or port 465?
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PWD)
        server.sendmail(GMAIL_USER, recipients, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
        raise


class Beeminder(object):

    AUTH_PARAMS = {'auth_token': AUTH_TOKEN}

    @classmethod
    def _get_data(cls, rel_url):
        full_url = 'https://www.beeminder.com/api/v1' + rel_url
        response = requests.get(full_url, params=cls.AUTH_PARAMS)
        return response.json()

    @classmethod
    def get_goals(cls):
        return cls._get_data('/users/me/goals.json')

    @classmethod
    def get_datapoints(cls, goal):
        url = '/users/me/goals/{}/datapoints.json'.format(goal['slug'])
        return cls._get_data(url)


def generate_daily_email_body(start_timestamp):
    end_timestamp = start_timestamp + ONE_DAY
    goals = Beeminder.get_goals()

    start_datetime = datetime.datetime.fromtimestamp(start_timestamp)
    end_datetime = datetime.datetime.fromtimestamp(end_timestamp)
    DT_FORMAT = "%m/%d %H:%M"

    res = 'Summary of your {} goals from {} to {}:\n\n'.format(
        len(goals), start_datetime.strftime(DT_FORMAT), end_datetime.strftime(DT_FORMAT)
    )

    for goal in goals:
        datapoints = Beeminder.get_datapoints(goal)
        today_datapoints = [dp for dp in datapoints if dp['timestamp'] >= start_timestamp and dp['timestamp'] < end_timestamp]

        res += '{}: {}'.format(goal['title'], len(today_datapoints))

    return res


start_timestamp = int(time.time()) - ONE_DAY

subject = 'Beeminder Daily Email - {}'.format(today)
email_body = generate_daily_email_body(start_timestamp)
print '------------------------------------------------'
print subject
print ''
print email_body
print '------------------------------------------------'
send_email(EMAIL_RECIPIENTS, subject, email_body)
