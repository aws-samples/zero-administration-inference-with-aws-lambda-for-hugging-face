"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from transformers import pipeline

summarizer = pipeline("summarization")

def handler(event, context):
    response = {
        "statusCode": 200,
        "body": summarizer(event['article'])[0]
    }
    return response