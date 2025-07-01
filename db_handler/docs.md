### Endpoint - "/get"

---

**Request:**

* **GET**
* **Headers** - None
* **Payload** -
```json
{
  "user": "<user-name>",
  "columns": [
    "col1",
    "col2",
    "..."
  ]
}
```
Not passing "columns" will the return all the columns for the user

**Response**:

* **Code**:
    * 200 - success
    * 204 - an error occurred while reading the database namely it's empty.
    * 404 - some columns in the payload are not in the database
    * 500 - an error while parsing the database has occurred.
* **Payload**: Returns the whole database as json of the following format:

```json
{
  "columns": [
    "col1",
    "col2",
    "..."
  ],
  "index": [
    "index1",
    "index2",
    "..."
  ],
  "data": [
    [
      "a",
      "b",
      "..."
    ],
    [
      "c",
      "d",
      "..."
    ],
    [
      "..."
    ]
  ]
}
```

, where each list in "data" is a row.

---

### Endpoint - "/commit"



**Request:**

* **POST**
* **Headers** - None
* **Payload** - A JSON of the following form

```json
{
  "user": "<username>",
  "datetime": "YYYY-MM-DD HH:MM:SS",
  "data": {
    "col1": "<data-point>",
    "col2": "<data-point>",
    "...": "..."
  }
}
```

**Response**:

* **Code**:
    * 201 - success.
    * 204 - an error occurred while reading the database, namely it's empty.
    * 404 - some columns in the payload are not in the database
    * 500 - an error has occurred while adding data to the database or while parsing the database
* **Payload**: None
