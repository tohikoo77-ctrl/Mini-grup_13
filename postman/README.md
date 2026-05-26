# Postman Collection

Generate a Postman collection from all Django URL patterns:

```bash
python scripts/export_postman_collection.py
```

For local backend:

```bash
python scripts/export_postman_collection.py --base-url http://127.0.0.1:8000
```

For PythonAnywhere:

```bash
python scripts/export_postman_collection.py --base-url https://deployminigroup13.pythonanywhere.com
```

The generated file is:

```text
postman/Mini-grup-13.postman_collection.json
```

Import that JSON file into Postman.

Swagger/OpenAPI endpoints:

```text
/api/schema/
/api/docs/
```

In Postman you can also import directly from:

```text
http://127.0.0.1:8000/api/schema/
```

or:

```text
https://deployminigroup13.pythonanywhere.com/api/schema/
```
