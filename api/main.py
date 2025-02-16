"""Main.py for FastAPI service to upload files, and shorten urls and return lists.  TODO: NEeds to handle spaces in userId for uploading files as that could scupper the URL downloads"""
import hashlib
import logging
import os
from typing import List, Annotated

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from fastapi import UploadFile, Header, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

app = FastAPI()
db_client = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

dynamo_table = os.environ["DYNAMODB_TABLE_NAME"]
s3_bucket = os.environ["S3_BUCKET_NAME"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)


class UrlToShorten(BaseModel):
    url: str


class ShortenedUrl(BaseModel):
    user_id: str
    url: str
    short_url: str


def add_url_to_table(user_id: str, url: str) -> str:
    # Hash the URL to get a random 8 character slug to shorten the URL
    data = url.encode()
    hash_obj = hashlib.sha3_256(data)
    random_slug = hash_obj.hexdigest()[:8]
    table = db_client.Table(dynamo_table)
    table.put_item(
        Item={
            "user_id": user_id,
            "url": url,
            "shortened-slug": random_slug
        }
    )
    return random_slug


def get_uploads_for_user(user_id: str) -> List[str]:
    table = db_client.Table(dynamo_table)

    # Grab the items for the provided user id
    response = table.query(KeyConditionExpression=Key("user_id").eq(user_id))
    return response['Items']


def add_file_to_s3(user_id: str, file: UploadFile):
    try:
        object_name = f"{user_id}/{file.filename.replace(' ', '_')}"
        # Upload the file to s3
        s3_client.upload_fileobj(file.file, s3_bucket, object_name, ExtraArgs={"ContentType": file.content_type})
        # no response object from upload_fileobj, so go find the url in the bucket
        bucket_location = s3_client.get_bucket_location(Bucket=s3_bucket)['LocationConstraint']
        url = f"https://{s3_bucket}.s3.{bucket_location}.amazonaws.com/{object_name}"
    except ClientError as e:
        logging.error(e)
        return ""
    else:
        return url

@app.get("/")
def root():
    return "Hello World"


@app.post("/shorten")
def shorten_url(user_id: Annotated[str, Header()], url: UrlToShorten | None = None) -> ShortenedUrl:
    """Shorten a given url
    :arg
        user_id (str): the user id of the user to save against
        url (str): the url to save
    :returns
        str: Shortened url
    """
    # Add the slug for the user-id to dynamo
    random_slug = add_url_to_table(user_id=user_id, url=url.url)

    # Return the shortened slug back to the user
    return ShortenedUrl(url=url.url, short_url=random_slug, user_id=user_id)


@app.post("/upload")
def upload_file(user_id: Annotated[str, Header()], file: UploadFile):
    """Add the file to S3 bucket and return a shortened version of the file
    :arg
        user_id (str): the user id of the user to save against
        file: (File): the file to save in S3
    :return
        str: Short url link to the file
    """

    # Add file to S3
    url = add_file_to_s3(user_id=user_id, file=file)
    # TODO: handle if url comes back blank
    # Add url to Dynamo
    random_slug = add_url_to_table(user_id=user_id, url=url)

    return ShortenedUrl(url=url, short_url=random_slug, user_id=user_id)


@app.get("/uploads")
def get_list_uploads(user_id: Annotated[str, Header()]):
    """Return a list of urls for a given user_id
    :arg
        user_id (str): the user id of the user to return the list of urls/files
    :return
        List[str]: List of short urls
    """

    return get_uploads_for_user(user_id)


handler = Mangum(app)
