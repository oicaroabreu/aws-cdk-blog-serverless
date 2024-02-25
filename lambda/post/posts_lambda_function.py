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

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
    }

    if http_method == "POST":

        if body:
            response = table.put_item(
                Item={
                    "id": ulid(),
                    "title": body["title"],
                    "text": body["text"],
                    "datetime": body["datetime"],
                    "user_id": body["user_id"],
                    "theme_id": body["theme_id"],
                }
            )

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(
                    {
                        "message": "Post Saved Successfully",
                    }
                ),
            }
        else:
            return {
                "statusCode": 400,
                "headers": headers,
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
                    "headers": headers,
                    "body": json.dumps(response["Item"]),
                }
        else:
            response = table.scan()
            if "Items" in response:
                return {
                    "statusCode": 200,
                    "headers": headers,
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
                UpdateExpression="set title = :t, #text = :tx, #dt = :dt, user_id = :uid, theme_id = :tid",
                ExpressionAttributeNames={"#dt": "datetime", "#text": "text"},
                ExpressionAttributeValues={
                    ":t": body["title"],
                    ":tx": body["text"],
                    ":dt": body["datetime"],
                    ":uid": body["user_id"],
                    ":tid": body["theme_id"],
                },
                ReturnValues="ALL_NEW",
            )

            if "Attributes" in response:
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps(
                        {
                            "message": "Post Saved Successfully",
                            "item": response["Attributes"],
                        }
                    ),
                }
        else:
            return {
                "statusCode": 400,
                "headers": headers,
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
                    "headers": headers,
                    "body": json.dumps(
                        {
                            "message": "Success",
                        }
                    ),
                }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(
            {
                "message": "Success",
            }
        ),
    }
