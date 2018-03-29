# reisbrein

Requires Python 3.4+ and Django 1.11+

## Installation

These instructions assume a Linux based OS.
For Windows installation instructions see [Install Windows](docs/install_windows.md).

### Get the code and create virtualenv

Get the code and enter the project directory,
```
git clone https://github.com/mathijsromans/reisbrein.git
cd reisbrein
```

Install dependencies,
```
sudo apt install virtualenv
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

### Install dependencies

Install python packages in the local env,
```
pip install -r requirements.txt
```

### Create local settings
There are some settings that are local and/or secret, these are set in `website/local_settings.py`.

Generate a `local_settings.py` file from the example,
```
python create_local_settings.py
```

### Create local database
Create a database (default is sqlite),
```
python manage.py migrate
```

## Run local server
Run the Django dev web server in the virtualenv (don't forget to active the virtualenv),
```
python manage.py runserver
```

The website is now available at http://127.0.0.1:8000 and admin interface at http://127.0.0.1:8000/admin.

## Configuration

To use various external APIs you need to use API keys. These keys are not part of the git sources, so you have to set them manually.
These kan be set in the file local_settings.py, which in first instance will be a copy of local_settings_example.py.

Note also that this file as a production server toggle, named 'PRODUCTION_SERVER', which by default is set to false.
This has the effect that a demo version of the external public transport planner will be used, which has a tight fair use policy.
Setting it to true will not help, because it only works on certain IP addresses.

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

## Tests
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

To log something, create a logger at the top of you python file,
```python
import logging
logger = logging.getLogger(__name__)
```

then create a log statement,
```python
logger.debug('an info log message')
logger.info('an info log message')
logger.warning('a warning log message')
logger.error('a error log message')
logger.exception(exception_object)
```
