# Installation Windows

## Installation

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

## Linux Virtual Machine

Follow instructions from https://www.lifewire.com/run-ubuntu-within-windows-virtualbox-2202098.

Proceed with installation instructions in the [README](README.md)
