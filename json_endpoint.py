import boto3
import json
import random
import os

s3 = boto3.client('s3')
bucket_name = os.environ['S3_BUCKET_NAME']
json_key = os.environ['JSON_KEY']

def lambda_handler(event, context):
    response = s3.get_object(Bucket=bucket_name, Key=json_key)
    json_data = json.loads(response['Body'].read().decode('utf-8'))
    
    query_params = event['queryStringParameters'] or {}
    item_id = query_params.get('id')
    
    if item_id:
        item = next((obj for obj in json_data if obj['id'] == item_id), None)
        if item:
            return {
                'statusCode': 200,
                'body': json.dumps(item),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    
    random_item = random.choice(json_data)
    return {
        'statusCode': 200,
        'body': json.dumps(random_item),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
