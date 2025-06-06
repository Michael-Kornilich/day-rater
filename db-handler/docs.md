## What

* IO with the database

## How

### Endpoint - "/"

* **Request:**
    * **GET**
    * **Payload** - None
* **Response**:
    * **Code**: 200 is success, 500 if an error while parsing the database has occurred.
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

* **Request:**
    * **POST**
    * **Payload**: A JSON of the following form

```json
{
  "index": "YYYY-MM-DD HH:MM:SS",
  "data": {
    "col1": "<data-point>",
    "col2": "<data-point>",
    "...": "..."
  }
}
```

* **Response**:
    * **Code**: 201 if success 500, if an error has occurred while adding data to the database.
    * **Payload**: None
