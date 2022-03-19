## Setup

```bash
pyenv virtualenv 3.9.11 vatglobal
pyenv activate vatglobal
```

## Updating

```bash
pip install pip-tools
pip-compile --output-file requirements.txt requirements.in
 ```

## Create a user
```bash
python manage.py createsuperuser
```

## Viewing data
```
python manage.py runserver
```
Testing URL: http://localhost:8000/api/transactions/retrieveRows/?date=2020%2F01%2F07&country=IT&currency=ZAR