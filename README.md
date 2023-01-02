``Simple-piccolo`` is a single-file application for quickly prototyping, exploring and testing ideas without any configuration, using Sqlite. The application use [FastAPI](https://fastapi.tiangolo.com/), [Piccolo ORM](https://piccolo-orm.readthedocs.io/en/latest/piccolo/getting_started/index.html) and [Piccolo Admin](https://piccolo-admin.readthedocs.io/en/latest/) for easy database interaction.

## How to use:

Clone the repository in a fresh virtualenv. 

Install dependencies
```
pip install -r requirements.txt
```

Start app
```
$ python app.py
```

After site is running log in as admin user on ``localhost:8000/admin/`` or go to ``http://localhost:8000/docs`` and use the FastAPI interactive API documentation.