# Zero administration :hugs: inference

### Note: This is not production code and simply meant as a demo

[:hugs: Transformers](https://huggingface.co/ ":hugs: Homepage") is a popular open-source project that provides pre-trained, state of the art Natural Language Processing (NLP) models for a wide variety of use cases. Customers with little to no machine learning experience can leverage pre-trained model to quickly enhance their applications using NLP. This includes tasks such as text classification, language translation, summarization, and question answering - to name a few.

While there is no shortage of model hosting options in today’s ML landscape, they each have trade-offs. Many customers are seeking a zero administration ML inference solution that allows quick prototyping. Striving to meet this need, this blog post introduces a low touch, cost effective, and scalable mechanism for hosting Hugging Face models for realtime inference using AWS Lambda.


This project shows how to serve [:hugs:](https://huggingface.co/ ":hugs: Homepage") inference.
* Serverless inference using a AWS Lambda with a custom container
* Stores custom container in Amazon Elastic Container Registry
* Pre-trained models are downloaded automatically from :hugs: the first time a model is used
* Pre-trained models are cached in Amazon Elastic File System to improve performance
* Builds with AWS Cloud Development Kit

## Architecture

![Architecture diagram](serverless-hugging-face.png)

## Getting Started
You need the following installed:
- git
- AWS CDK
- Python 3.6+
- A virtual env (optional)

Clone the project:
```
$ git clone https://github.com/CyranoB/serverless-hugging-face.git && cd serverless-hugging-face
```

## Instructions
Install the required dependencies
```
$ pip install -r requirements.txt
```

Bootstrap the CDK

```
$ cdk bootstrap
```

And deploy.

```
$ cdk deploy
```

## Code structure
The code is organized the following way:
```bash
├── inference
│   ├── Dockerfile
│   ├── sentiment.py
│   └── summarization.py
├── app.py
└── ...
```

The ``ìnference``` directory contains:
- The Dockerfile used to build a custom image to be able to run :hugs: inference using PyTorch using Lambdas
- The Python scripts doing the actual inference

The CDK script will generate for each Python scripts in the ```inference``` directory a Lambda function backed by the custom container and the Python inference script.


## Adding a translator (optional)

You can add more model by simply adding the Python script in the ``ìnference```directory

For example, add the following code in a file called ```translate-en2fr.py```
```python
import json
from transformers import pipeline

en_fr_translator = pipeline('translation_en_to_fr')

def handler(event, context):
    response = {
        "statusCode": 200,
        "body": en_fr_translator(event['text'])[0]
    }
    return response
```
Then run:
```bash
$ cdk synth
$ cdk deploy
```

This will create a new enpoint to perform English to French tranlastion.

## Cleaning up

After you experiment with this project you should run ```cdk destroy``` to destroy all the infrastructure we created and avoid incurring in extra charges.


## License

This project is licensed under the Apache-2.0 License.

Disclaimer: Deploying the demo applications contained in this repository will potentially cause your AWS Account to be billed for services.

## Links
- [:hugs:](https://huggingface.co)
- [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)
- [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon Elastic File System](https://aws.amazon.com/efs/)
