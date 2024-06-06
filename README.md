## Serverless Application for CSV to JSON Transformation and Serving

### Overview

This project aims to create a serverless application within an AWS environment that periodically retrieves a CSV file from a URL, stores it in an S3 bucket, transforms its content into a JSON feed, and efficiently serves individual objects from this feed via a query string. The response is cached to handle high-volume traffic.

### Assumptions

- The JSON file generated from the CSV data is assumed to be a single file stored in S3.
- The application assumes the JSON file size is manageable for Lambda functions to parse and serve. For significantly larger files, consider alternative approaches for efficient processing and retrieval.

### Project Components

1. **Lambda Function to Retrieve and Store CSV as JSON**
2. **Lambda Function to Serve JSON Data**
3. **AWS S3**: For storing JSON files.
4. **AWS API Gateway**: For creating endpoints.
5. **AWS CloudFront**: For caching responses.
6. **AWS CloudWatch**: For scheduling periodic execution.

### Prerequisites

- AWS account with necessary permissions.
- S3 bucket created for storing JSON files.
- Environment variables set in AWS Lambda functions.

### Environment Variables

1. **S3_BUCKET_NAME**: The name of the S3 bucket where JSON files will be stored.
2. **CSV_URL**: The URL of the CSV file to be downloaded.
3. **JSON_KEY**: The prefix for the JSON file name (e.g., `data`).

### Lambda Function to Retrieve CSV and Store as JSON in S3

Create a Lambda function with the following code to download the CSV, convert it to JSON, and store it in an S3 bucket:

```python
import boto3
import csv
import json
import requests
import uuid
import os
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = os.environ['S3_BUCKET_NAME']
csv_url = os.environ['CSV_URL']
json_key_prefix = os.environ['JSON_KEY']

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
    
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    json_key = f"{json_key_prefix}_{timestamp}.json"
    
    s3.put_object(Bucket=bucket_name, Key=json_key, Body=json_body, ContentType='application/json')
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV successfully processed and stored as JSON in S3')
    }
```

### Lambda Function to Serve JSON Data

Create another Lambda function to retrieve and serve the JSON data based on a query string parameter:

```python
import boto3
import json
import random
import os

s3 = boto3.client('s3')
bucket_name = os.environ['S3_BUCKET_NAME']
json_key_prefix = os.environ['JSON_KEY']

def get_latest_json_key(bucket_name, prefix):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    all_keys = [content['Key'] for content in response.get('Contents', [])]
    if not all_keys:
        return None
    latest_key = max(all_keys)
    return latest_key

def lambda_handler(event, context):
    json_key = get_latest_json_key(bucket_name, json_key_prefix)
    if not json_key:
        return {
            'statusCode': 404,
            'body': json.dumps('No data found'),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
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
```

### Setting Environment Variables in AWS Lambda

1. Go to the AWS Lambda console.
2. Select your Lambda function.
3. Click on the "Configuration" tab.
4. Scroll down to the "Environment variables" section.
5. Click "Edit" and add the necessary environment variables.

### CloudWatch Event Rule

Create a CloudWatch Event rule to trigger the first Lambda function every 60 minutes:

1. Go to the CloudWatch console.
2. Create a new rule with a schedule expression of `rate(60 minutes)`.
3. Add the first Lambda function as the target.

### Warning

Handling large JSON files may require a different approach to ensure efficient processing and retrieval. Larger files can lead to longer processing times and higher latency. Consider using pagination, partitioning, or storing data in a database for better performance with large datasets.

### Conclusion

This setup ensures that your serverless application periodically retrieves the CSV file, transforms it into JSON, stores it in S3, and serves individual objects efficiently with caching to handle high-volume traffic. Make sure to test and monitor the application to handle any edge cases or scaling issues effectively.
