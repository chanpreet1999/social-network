
# Social Network Django Application

This is a Django-based social network application with functionalities for user signup, login, sending friend requests, accepting/rejecting friend requests, and searching for users as specified in the [requirement document](https://drive.google.com/file/d/1zjNqjpcvJG843RnJk9Y_CqPLb5tVBuL1/view)

## Features
  
- User Signup and Login

- Search Users by Email and Name

- Send, Accept, and Reject Friend Requests

- List Friends and Pending Friend Requests

## Prerequisites

- Python 3

- Docker and Docker Compose installed on your machine(for running in a docker image)

  

## Installation

  

### Clone the Repository

```sh

git clone https://github.com/yourusername/social_network.git

cd social_network

pip install -r requirements.txt

```

### Run the Application using Python
```sh
python manage.py runserver
```

### Run the Application using Docker

```sh
docker-compose build
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
docker-compose up
```

## Database
For the  sake of simplicity the application uses the default SQLite database.

Some entries have already been created in the database. Please refer to the examples in swagger/postman collection


## Documentation
### Postman
For API testing, you can use the provided Postman collection. You can download it from [here](./documentation/postman_collection.json).

### Swagger
You can also copy the swagger file [here](./documentation/swagger.yaml) and paste it in [swagger editor](https://editor.swagger.io/ ) to get the swagger documentation

