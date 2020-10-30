import json
import boto3
from os import environ

AWS_ACCESS_KEY_ID = environ['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = environ['aws_secret_access_key']
AWS_REGION_NAME = 'us-east-1'
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/..."
QUEUE_VISIBILITY_TIMEOUT_SECONDS = 30

COMMON_SQS_AND_ELASTIC_KEY = "SomeId"


class SqsMessage:
    def __init__(self):
        self.session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                     region_name=AWS_REGION_NAME)
        self.sqs = self.session.client('sqs')

    def _receive_message(self):
        # Receive message from SQS queue
        response = self.sqs.receive_message(
            QueueUrl=QUEUE_URL,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=QUEUE_VISIBILITY_TIMEOUT_SECONDS,
            WaitTimeSeconds=0
        )

        try:
            _message = response['Messages'][0]
        except KeyError:
            return None

        return _message

    def receive_all_messages(self):
        all_messages = []
        while True:
            _message_resp = self._receive_message()
            if not _message_resp:
                break
            all_messages.append(_message_resp)

        return all_messages


def parse_attribute_from_message(message, attribute_name):
    message_body_dict = json.loads(message["Body"])
    message_dict = json.loads(message_body_dict["Message"])
    message_resource_dict = message_dict.get("resource")
    try:
        return message_resource_dict[attribute_name]
    except KeyError as key_err:
        raise key_err


def get_dsl_query_filter_base():
    return {
        "bool": {
            "should": None,
        }
    }


def add_item_to_dsl_query_filter_should(item):
    elastic_dsl_should = {
        "term": {
            COMMON_SQS_AND_ELASTIC_KEY: str(item)
        }
    }
    return elastic_dsl_should


if __name__ == "__main__":
    message = SqsMessage()
    received_messages = message.receive_all_messages()
    print('Received %s messages' % len(received_messages))

    attribute_found_items_list = []
    for received_message in received_messages:
        attribute_found_items_list.append(parse_attribute_from_message(received_message,
                                                                       COMMON_SQS_AND_ELASTIC_KEY))

    should_items_list = []
    for item in attribute_found_items_list:
        should_items_list.append(add_item_to_dsl_query_filter_should(item))

    elastic_dsl_base_query = get_dsl_query_filter_base()
    elastic_dsl_base_query["bool"]["should"] = should_items_list

    print('Add this JSON to DSL query filter in your Kibana search:')
    print('--------------------------------------------------------')
    print(json.dumps(elastic_dsl_base_query))
