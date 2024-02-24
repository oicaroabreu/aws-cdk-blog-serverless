import json
import os
import boto3
from ulid import ulid
from botocore.exceptions import ClientError


def handler(event, context):

    http_method = event["httpMethod"]
    path_params = event["pathParameters"]

    theme_id = None
    if path_params and "id" in path_params:
        theme_id = path_params["id"]

    table_name = os.environ["THEMES_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    body = None
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    if http_method == "POST":

        if body:

            response = table.put_item(
                Item={
                    "id": ulid(),
                    "name": body["name"],
                },
            )
            print(response)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Theme Saved Successfully",
                    }
                ),
            }

        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }

    elif http_method == "GET":
        if theme_id:
            response = table.get_item(Key={"id": theme_id})
            if "Item" in response:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(response["Item"]),
                }
        else:
            response = table.scan()
            if "Items" in response:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(response["Items"]),
                }

    elif http_method == "PUT":

        if body:
            response = table.update_item(
                Key={"id": theme_id},
                UpdateExpression="set #n = :n",
                ExpressionAttributeNames={"#n": "name"},
                ExpressionAttributeValues={
                    ":n": body["name"],
                },
                ReturnValues="ALL_NEW",
            )
            print(response)

            if "Attributes" in response:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(
                        {
                            "message": "Theme Saved Successfully",
                            "item": response["Attributes"],
                        }
                    ),
                }

        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Bad Request",
                    }
                ),
            }

    elif http_method == "DELETE":
        response = table.delete_item(Key={"id": theme_id})

        if "ResponseMetadata" in response:
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"message": "Success"}),
                }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Success"}),
    }
