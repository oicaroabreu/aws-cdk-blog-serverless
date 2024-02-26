import datetime
import json
import time
import os
import boto3
from ulid import ulid
from botocore.exceptions import ClientError


def get_current_datetime():

    utc_now = datetime.datetime.utcnow()
    brt_offset = datetime.timedelta(hours=-3)
    saopaulo_time = utc_now + brt_offset

    return saopaulo_time.strftime("%Y-%m-%dT%H:%M:%SZ%z")


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
                    "datetime": get_current_datetime(),
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
                return {
                    "statusCode": 404,
                    "headers": headers,
                    "body": json.dumps(
                        {
                            "message": "No item found",
                        }
                    ),
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
                UpdateExpression="set title = :t, #text = :tx, user_id = :uid, theme_id = :tid",
                ExpressionAttributeNames={"#text": "text"},
                ExpressionAttributeValues={
                    ":t": body["title"],
                    ":tx": body["text"],
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
        try:
            response = table.get_item(Key={"id": post_id})
            if "Item" in response:
                response = table.delete_item(Key={"id": post_id})
                print(response)
                if "ResponseMetadata" in response and response["ResponseMetadata"]["HTTPStatusCode"] ==  200:
                    return {
                        "statusCode":  200,
                        "headers": headers,
                        "body": json.dumps({"message": f"Post {post_id} Deleted Successfully"}),
                    }
            else:
                return {
                    "statusCode": 404,
                    "headers": headers,
                    "body": json.dumps(
                        {
                            "message": "No item found",
                        }
                    ),
                }
        except Exception as e:
            return {
                "statusCode":  500,
                "headers": headers,
                "body": json.dumps({"message": "Internal Server Error"}),
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
