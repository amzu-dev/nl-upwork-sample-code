import boto3
import csv
import json
import requests
import uuid
import os

s3 = boto3.client('s3')
bucket_name = os.environ['S3_BUCKET_NAME']
csv_url = os.environ['CSV_URL']
json_key = os.environ['JSON_KEY']

def lambda_handler(event, context):
    response = requests.get(csv_url)
    response.raise_for_status()
    
    csv_data = response.content.decode('utf-8').splitlines()
    csv_reader = csv.DictReader(csv_data)
    
    json_data = []
    for row in csv_reader:
        row['id'] = str(uuid.uuid4())
        json_data.append(row)
    
    json_body = json.dumps(json_data)
    
    s3.put_object(Bucket=bucket_name, Key=json_key, Body=json_body, ContentType='application/json')
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV successfully processed and stored as JSON in S3')
    }
