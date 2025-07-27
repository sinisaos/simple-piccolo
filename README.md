``Simple-piccolo`` is a single-file application for quickly prototyping, exploring and testing ideas without any configuration, using Sqlite. The application use [FastAPI](https://fastapi.tiangolo.com/) or [Litestar](https://litestar.dev/) or [Lihil](https://www.lihil.cc/), [Piccolo ORM](https://piccolo-orm.readthedocs.io/en/latest/piccolo/getting_started/index.html) and [Piccolo Admin](https://piccolo-admin.readthedocs.io/en/latest/) for easy database interaction.

## How to use:

Clone the repository in a fresh virtualenv. 

Install dependencies
```
pip install -r requirements.txt
```

You can choose between three router frameworks, **FastAPI** or **Litestar** or **Lihil**. 

For starting **FastAPI** you can use:
```
$ python fastapi_app.py
```
For starting **Litestar** you can use:
```
$ python litestar_app.py
```
For starting **Lihil** you can use:
```
$ python lihil_app.py
```

After site is running log in as admin user on ``http://localhost:8000/admin/`` or go to ``http://localhost:8000/docs`` and use the **FastAPI** or **Lihil** interactive API documentation. For **Litestar** go to ``http://localhost:8000/schema/swagger`` and use the **Litestar** interactive API documentation or log in as admin user on ``http://localhost:8000/admin/``.