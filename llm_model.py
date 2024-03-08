import openai
import os
import requests
import re
import json
import yaml


# The keys will be pulled form the azure app service configuration
api_key = os.getenv("API_KEY", default="default_secret_key")
search_key = os.getenv("SEARCH_KEY", default="default_secret_key")

openai.api_type = "azure"
openai.api_version = "2023-09-01-preview"
openai.api_base = "https://stefan-model-testing.openai.azure.com/"
openai.api_key = api_key
deployment_id = "gpt-4-32k"

serach_endpoint = "https://aitechtalkbitola.search.windows.net"
search_key = search_key
search_index_name = "aitechtalkbitola"


def generate_response(prompt):
    system_message = "Hi!, I am Mr.Stu. AI powered API assistant developed by Micky and Stefan. To help them make a great impression on the Pelister Tech in Bitola"

    # Send request to OpenAI API to get the model's reponse
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        deployment_id=deployment_id,
        dataSources=[
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": serach_endpoint,
                    "indexName": search_index_name,
                    "semanticConfiguration": "default",
                    "queryType": "simple",
                    "fieldsMapping": {},
                    "inScope": True,
                    "roleInformation": system_message,
                    "strictness": 5,
                    "topNDocuments": 5,
                    "key": search_key
                }
            }
        ],
        temperature=0,
        top_p=1,
        max_tokens=2000
    )

    # Extract the message from the reponse
    message = completion["choices"][0]["message"]["content"]
    return message


def setup_bring_your_own_data(deployment_id: str) -> None:
    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{
                deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )
    openai.requestssession = session


setup_bring_your_own_data(deployment_id)


def extract_json_yaml_code(response):
    matches = re.search(r'```(json|yaml)(.*?)```', response, re.DOTALL)
    if matches:
        format, content = matches.groups()
        content = content.strip()
        if format == 'json':
            try:
                content_dict = json.loads(content)
                return json.dumps(content_dict, indent=2)
            except json.JSONDecodeError as err:
                raise Exception(f"Error validating JSON content: {str(err)}")
        elif format == 'yaml':
            try:
                content_dict = yaml.safe_load(content)
                return yaml.dump(content_dict, default_flow_style=False, indent=2)
            except yaml.YAMLError as err:
                raise Exception(f"Error validating YAML content: {str(err)}")
    else:
        return response
