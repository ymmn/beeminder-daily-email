# beeminder-daily-email

Sends a daily summary email of your goals on Beeminder.

1) Clone this repo

2) Edit `settings.json` to have your correct values

3) Add a cron job to call this script everyday
```
crontab -e

# edit the path to point to the repo correctly
# this will trigger the email to be sent everyday at 1AM
0 1 * * * python /path/to/repo/send-daily-email.py 
```
