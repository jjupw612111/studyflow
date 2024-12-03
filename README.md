# study-helper
CS 310 Final Project Fall '24

# organization
/client:
- main.py
- docker stuff goes here
- client-config.ini stuff

/server:
- folders for each aws lambda function
- eg. `/server/upload`, `/server/users`, `/server/merge`, etc
- each of those folders will have the aws lambda code, including:
  - `datatier.py`
  - `lambda_function.py`
  - `config.ini`
  - `test.txt`

