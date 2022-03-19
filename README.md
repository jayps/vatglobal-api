# Transaction API

This API imports transactions from a CSV and allows users to list transactions by country and date while allowing for
currency conversion.

# Development

## Prerequisites

In order to run this API, you just need [docker](https://www.docker.com/)
and [docker-compose](https://docs.docker.com/compose/install/) installed.

## Running the code

Run the code with

```bash
docker-compose up
```

## Running tests

Run tests with

```bash
docker-compose -f docker-compose.test.yml up
```

## Updating dependencies

If you need to update dependencies in the application, use `pip-tools` and add the new packages to `requirements.in`.  
I recommend using a virtual environment for this. I personally use [PyEnv](https://github.com/pyenv/pyenv)
and [PyEnv VirtualEnv](https://github.com/pyenv/pyenv-virtualenv). This just helps you to use the correct version of
Python.

```bash
pyenv virtualenv 3.9.11 venv
pyenv activate venv
pip install pip-tools
pip-compile --output-file requirements.txt requirements.in
 ```

# Viewing information

Once the API is up and running, you can view information at [http://localhost:8000/admin](http://localhost:8000/admin).
You'll need a user account to log in to view information there. Run the following to create a new user:

```bash
docker exec -it vatglobal-api python manage.py createsuperuser
```

# Endpoints

## processFile

Endpoint: `POST http://localhost:8000/api/transactions/processFile/`  
Use this endpoint to upload a CSV file. There's one included in the `instruction` directory.

### Inputs:

`file`: **Required**. The CSV file that you're uploading  
`skip_errors`: **Optional**. Boolean field. If set to `true`, the processor will skip over fields that are invalid (ie.
where the type is incorrect or a date is not of the right format, etc). The detault here is `false`.  
Note that the content type header for this endpoint should be `multipart/form-data`.

## retrieveRows

Endpoint: `GET http://localhost:8000/api/transactions/retrieveRows/`
Use this endpoint to retrieve transactions.

### Inputs

Some filters are available via query parameters.  
`date`: **Required**. Date field, in the format `YYYY/MM/DD`.   
`country`: **Required**. Country code, in [ISO-3166-1 alpha-2](https://datahub.io/core/country-list#data) format.   
`currency`: **Optional**. Currency code, in [ISO-4217](https://datahub.io/core/currency-codes#data) format. **NOTE**: If the conversion that you are requesting is unavailable, the call will fail with a 404 status code. I figured this is better than returning data incorrectly without conversions - if you want the data without conversion, you could just omit the currency code.

**Example**: [http://localhost:8000/api/transactions/retrieveRows/?date=2020%2F01%2F07&country=IT&currency=ZAR](http://localhost:8000/api/transactions/retrieveRows/?date=2020%2F01%2F07&country=IT&currency=ZAR)
.

# Challenges

One of the challenges proposed in this exercise was to be gentle on the banking API used to fetch exchange rates. To
solve for this problem, I've stored any data that we fetch from their API in the local database for this API.  
This should be fine since it's historical data that is _extremely_ unlikely to change. So when we query for an exchange
rate on a particular date, we check the local database first. If we don't have the information, we fetch it and store it
locally for the next time we might need it.  
An alternate solution to this might have been something like a redis cache, but I chose the database solution since the
data is so unlikely to change.

# Improvements

This API handles small datasets - the testing CSV file in the `instructions` folder only has just over 1K transactions
in it. I tested with up to 20K transactions and things started to get a little slow.  
For a speed improvement, I might recommend a few different approaches:

- If it's possible to ingest data through other sources, running multiple instances of the API as microservices and
  allowing other entities to send transaction information to the API might be a good idea. Horizontal scaling enables us
  to receive large volumes of data over time with fair ease.
- If the information is only available in CSV format as it is in this exercise, then the above solution won't work. In
  that case, I would recommend one of two solutions:
    - Multithreading: This isn't something that I've had great experience with in Python, but it could work. If we have
      enough CPU power available, we could divide the work into chunks and send it off to multiple CPUs.
    - Queueing: **This is the solution I would recommend**. Reading a large file isn't a problem - processing large
      amounts of data is where the problem sits. To solve that, I would use a queueing mechanism. This is similar to
      multithreading/multiprocessing on the face of it, but I've found better success with this in the past. Queueing
      would also work pretty well with running multiple instances of this API as microservices.    - The process would look something like this:
        - Upload a file
        - Read the file line by line
        - Add each line into a queue
        - Have a whole separate process pick up jobs from the queue and process information

# Other potential improvements
There are a few other things that I would improve on this project:
- Automated docs: It's nice to have self documenting code. I generally use [drf-yasg](https://drf-yasg.readthedocs.io/en/stable/) for that. 
- Better use of filters: the [django-filter](https://django-filter.readthedocs.io/en/stable/) package allows for some cool filtering capabilities. I wrote very manual code for filters in this demo. `django-filter` would have allowed for cleaner code in terms of filtering for the retrieval endpoint.
- Helm charts/K8s manifests: I've not added it here, but we could easily deploy this to k8s or some other scalable cloud solution so that we can scale horizontally with fair ease. '
- Better automation and management: You need knowledge of things like pip-tools and docker-specific ways of executing things in a container. I prefer having a single tool to address most of (or all of) our needs - something like a makefile, although I'm not a fan of those since that's just _anoooother_ tool. I think it's just nice for very junior developers to be able to use a single tool to manage things, focussing only on the code and avoiding tool-fatigue.