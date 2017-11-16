# reisbrein

Requires Python 3.4+ and Django 1.11+

## Installation part 1 (Linux)

Get the code and enter the project directory,
```
git clone https://github.com/bartromgens/django-project-template.git
cd django-project-template
```

Install dependencies that you will need,
```
apt-get install virtualenv
```
or
```
pip install virtualenv
```

Create a virtual environment,
```
virtualenv -p python3 env
```

Activate the virtualenv (always do this before working on the project),
```
source env/bin/activate
```

Make sure you have a recent version of pip,
```
pip install --upgrade pip
```

## Installation part 1 (Windows)

Install git for windows from
https://git-scm.com/download/win.
Choose default options.

Install python for windows from
https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64-webinstall.exe.
Before you install, make sure you check "add Python to PATH"!

Check that python works:
Run program GIT Bash
```
python --version
```
Outcome should be:
```
Python 3.6.3
```

Download TortoiseGit (this is optional: you can also directly use GIT Bash or GIT Gui)
from https://tortoisegit.org.

Create directory reisbrein
In the directory, right click on an empty space and choose Git Clone...
source: https://github.com/mathijsromans/reisbrein.git
Note that you get a double directory reisbrein/reisbrein. This is good.

Enter the reisbrein/reisbrein directory. Right-click and choose Run Git Bash Here.

Make sure you have a recent version of pip,
```
pip install --upgrade pip
```

Install virtualenv
```
pip install virtualenv
```

Create a virtual environment,
```
virtualenv env
```

Activate the virtualenv (always do this before working on the project),
```
source env/Scripts/activate
```

## Installation part 2 (Windows and linux)

Install python packages in the local env,
```
pip install -r requirements.txt
```

Generate a `local_settings.py` file from the example,
```
python create_local_settings.py
```

Create a database (default is sqlite),
```
python manage.py migrate
```

#### Run a developement webserver
Run the Django dev web server in the virtualenv (don't forget to active the virtualenv),
```
python manage.py runserver
```

The website is now available at http://127.0.0.1:8000 and admin http://127.0.0.1:8000/admin.

## Configuration (optional)

#### Create a superuser (optional)
This allows you to login at the website as superuser and view the admin page,
```
python manage.py createsuperuser
```

#### local_settings.py

The local settings are defined in `website/local_settings.py`. 
These are not under version control and you are free change these for your personal needs.
This is also the place for secret settings. An example, on which this file is based, is found in `website/local_settings_example.py`.

#### Daily backups (cronjob)
This project has a django-cronjob that makes daily backups of the raw database (includes everything), and a json dump of the data.
These are defined in `website/cron.py`. The location of the backup files is defined in `website/local_settings.py`. 
Create the following cronjob (Linux) to kickstart the `django-cron` jobs,
```
$ crontab -e
*/5 * * * * source /home/<username>/.bashrc && source /home/<path-to-project>/env/bin/activate && python /home/<path-to-project>/website/manage.py runcrons > /home/<path-to-project>/log/cronjob.log
```

## Testing

Run all tests,
```
python manage.py test
```

Run specific tests (example),
```
python manage.py test website.tests.TestCaseAdminLogin
```

## Logging
There are 3 log files (`debug.log`, `error.log`, `django.log`) available, with different log levels and for different applications.
The log files are found in the `log` directory of the project.
The log statements contain the time, log level, file, class, function name and line. 

The log something, create a logger at the top of you python file,
```python
import logging
logger = logging.getLogger(__name__)
```
then create a log statement as follows,
```python
logger.debug('an info log message')
logger.info('an info log message')
logger.warning('a warning log message')
logger.error('a error log message')
logger.exception(exception_object)
```
