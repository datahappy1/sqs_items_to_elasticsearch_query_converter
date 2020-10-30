# sqs_to_kibana_query_filter_helper
This helper tool polls for messages in a specified AWS SQS queue, filters these messages by a "key" name declared as a variable, and returns Elastic DSL query filter JSON for your Kibana search. The returned JSON lets you search for all of these keys in your Elasticsearch index at once using a `should` statement.

# How to run this tool:
1) Git clone this tool and ideally setup a Pipenv or a plain virtual environment.
2) Setup these environment variables with your AWS access key ID and the secret access key:
    - `aws_access_key_id`
    - `aws_secret_access_key`
3) Setup these variables in `__main__.py`:
    - `AWS_REGION_NAME` string, for example: `us-east-1`
    - `QUEUE_URL` string, for example: `https://sqs.us-east-1.amazonaws.com/123456789012/MyQueue`
    - `QUEUE_VISIBILITY_TIMEOUT_SECONDS` integer, i.e `30` seconds of visibility timeout
    - `COMMON_SQS_AND_ELASTIC_KEY` string, for example `PersonId` ( This is a key in your data that has to be common for the SQS message body and the indexed field in your Elasticsearch index )
4) Run the `__main__.py` script
5) Paste the returned JSON in your Kibana search filter DSL query "EDIT FILTER" input  ![](/docs/img/DSL_query_filter.PNG)

# Useful links:
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html
- https://www.elastic.co/guide/en/elasticsearch/reference/7.9/query-filter-context.html
