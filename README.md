# Page analyzer
[Hexlet](https://ru.hexlet.io/) study project. Page analyzer web application for SEO optimization. 
### [Link to live app](https://page-analyzer-ku65.onrender.com/)

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Jickx/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Jickx/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/ba786c33385dc7cea68f/maintainability)](https://codeclimate.com/github/Jickx/python-project-83/maintainability)

## Getting Started

### Clone the current repository:
```git clone https://github.com/Jickx/python-project-83```

### Requirements:
* poetry = "1.6.1"
* python = "^3.10"
* flask = "^2.3.3"
* PostgreSQL = "15.4"
* gunicorn = "^20.1.0"
* psycopg2-binary = "^2.9.7"
* python-dotenv = "^1.0.0"
* validators = "^0.21.2"
* url-normalize = "^1.4.3"
* requests = "^2.31.0"
* bs4 = "^0.0.1"


## Installation guide

### Makefile

Install poetry project: ```make install```

Install poetry project and start postgresql server: ```make build```

Run flask app: ```make dev```

Start gunicorn server: ```make dev```

### Installation:
* [Install PostgreSQL](https://www.postgresql.org/download/)
*  Start PostgreSQL server: ```brew services start postgresql@15```
* [Install Poetry.](https://python-poetry.org/docs/)
* Install project and start postgresql server: ```make build```


### Run:
* Start gunicorn server: ```make start```
* Go to: ```http://127.0.0.1:5000```

## How to use:
1. Open app homepage.
2. Enter webpage address.
3. Run analyzer tests.
4. Result with response code, H1 tag, title, description and date of creation will appear if test was successful.
5. it is possible to run tests multiple times.
