import json
import os
import boto3
from ulid import ulid
from botocore.exceptions import ClientError


def handler(event, context):

    http_method = event["httpMethod"]
    path_params = event["pathParameters"]

    post_id = None
    if path_params and "id" in path_params:
        post_id = path_params["id"]

    body = None
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    table_name = os.environ["POSTS_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    if http_method == "POST":

        if body:
            response = table.put_item(
                Item={
                    "id": ulid(),
                    "title": body["title"],
                    "message": body["message"],
                    "datetime": body["datetime"],
                    "user_id": body["user_id"],
                    "theme_id": body["theme_id"],
                }
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "Post Saved Successfully",
                }),
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
        if post_id:
            response = table.get_item(Key={"id": post_id})
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

        # def get_posts_by_theme(theme_id):
        # dynamodb = boto3.resource("dynamodb")
        # table = dynamodb.Table("posts_table")

        # response = table.scan(
        #     FilterExpression=Attr("theme_id").eq(theme_id)
        # )

        # if "Items" in response:
        #     return response["Items"]
        # else:
        #     return []

    elif http_method == "PUT":
        if body:
            response = table.update_item(
                Key={"id": post_id},
                UpdateExpression="set title = :t, message = :m, #dt = :dt, user_id = :uid, theme_id = :tid",
                ExpressionAttributeNames={"#dt": "datetime"},
                ExpressionAttributeValues={
                    ":t": body["title"],
                    ":m": body["message"],
                    ":dt": body["datetime"],
                    ":uid": body["user_id"],
                    ":tid": body["theme_id"],
                },
                ReturnValues="ALL_NEW",
            )

            if "Attributes" in response:
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(
                        {
                            "message": "Post Updated Successfully",
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
        response = table.delete_item(Key={"id": post_id})

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
