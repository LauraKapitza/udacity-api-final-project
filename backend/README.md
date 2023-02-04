# Documentation API

## Categories Route

### `GET '/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Response schema:

```
{
  "success": <Boolean>,
  "categories": Dict<string, string>,
  "total_categories": <int>
}
```

- Response example:

```json
{
  "success": true,
  "total_categories": 6,
  "categories": {
      "1": "Science",
      "2": "Art",
      "3": "Geography",
      "4": "History",
      "5": "Entertainment",
      "6": "Sports"
  }
}
```

### `GET '/categories/${category_id}/questions'`

- Returns a list of paginated question whose categories match a given category id.
- Request Query: 
  - page - integer (optional) 
- Request Parameter: 
  - category - integer (optional)
- Response schema:

```
{
  "success": <Boolean>,
  "questions: List<Dict>,
  "total_questions": <int>
}
```

- Response example:

```json
{
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        }
    ],
    "success": true,
    "total_questions": 19
}
```


## Questions Route


### `GET '/questions'`

- Fetches a list of paginated questions as well as a dictionary of categories.
- Request Query: 
  - page (optional)
- Response schema:

```
{
  "success": <Boolean>,
  "questions: List<Dict>,
  "total_questions": <int>
  "categories": Dict<string, string>,
  "current_category": <str>
}
```

- Response example:

```json
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": "Science",
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        }
    ],
    "success": true,
    "total_questions": 19
}
```

### `DELETE '/questions/${question_id}'`

- Deletes a question by its given id
- Request Parameter: 
  - question id (required)
- Response schema:

```
{
  "success": <Boolean>,
  "deleted": <int>
  "message": <str>
}
```

- Response example:
```json
{
    "success": true,
    "deleted": 1,
    "message": "Question was successfully deleted."
}
```

### `POST '/questions'`

- Creates a question with given properties
- Request body: 
  - question (required)
  - answer (required)
  - difficulty (required)
  - category (required)
- Response schema:

```
{
  "success": <Boolean>
}
```

- Response example:
```json
{
    "success": true
}
```

### `POST '/questions/search'`

- Returns a list of paginated question whose title matches a given search term.
Also, it returns the current category of the first question in the list.
- Request body:
  - page (optional)
  - searchTerm (required)
- Response schema:

```
{
  "success": <Boolean>,
  "questions: List<Dict>,
  "total_questions": <int>
  "current_category": <str>
}
```

- Response example:

```json
{
    "current_category": "Entertainment",
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        }
    ],
    "success": true,
    "total_questions": 19
}
```



## Quizzes Route

### `POST '/quizzes'`


- Returns a random question by a given category that is not included in a given previous question list.
- Request body:
  - previous_questions (required)
  - quiz_category (required)
- Response schema:

```
{
  "success": <Boolean>,
  "question: <Dict>,
}
```

- Response example:

```json
{
    "question": {
        "answer": "Tom Cruise",
        "category": 5,
        "difficulty": 4,
        "id": 4,
        "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    "success": true
}
```