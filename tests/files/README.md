# Test files

Test files are divided up into 2 types of tests. They follow a naming schema that follows `(Number)(Type).yaml` Where number is just a ever increasing integer and Type is different depending on the test type. Each type of test should be counted seperatly.

- Successfull tests. Type: 's'
- Failing tests. Type: 'f'



# Successfull tests

Files in `success` folder.

Each file should contain a top level dict with the keys `data` and `schema` where the test data should exists.



# Failing tests

Files in `fail` folder.

Each file should contain a top level dict with the keys `data`, `schema` and `errors` where the test data should exists.



# cli tests

Simple schema and data files that is used to test input of files via cli.



# partial schemas

Files used to test partial schema support.
