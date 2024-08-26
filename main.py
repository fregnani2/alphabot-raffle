
import os
from flask import Flask, jsonify, Response
import requests
import logging
import sys
from dotenv import load_dotenv
import json 

load_dotenv()
app = Flask(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

API_KEY = os.getenv('API_KEY')



def get_slugs():
    page = 0
    all_data = []
    while True:
        query_params = {'filter': 'unregistered', 'status': 'active', 'scope': 'community', 'pageSize': 50, 'pageNum': page}
        res = requests.get(url='https://api.alphabot.app/v1/raffles', headers={'Authorization': f'Bearer {API_KEY}'}, params=query_params)
        data = res.json()
        if data['success'] == False:
            raise Exception('Failed to get raffles -- Reason:' + f'{data["errors"][0]["message"]}')
        for item in data['data']['raffles']:
            all_data.append(item['slug'])
        if data['data']['finalPage'] == True:
            break
        page += 1
    return all_data

@app.route('/raffles', methods=['GET'])
def get_raffles():
    try:
        slugs = get_slugs()
        return Response(json.dumps(slugs, indent=4), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, indent=4), mimetype='application/json')

@app.route('/register', methods=['GET'])
def register_raffles():
    try:
        all_data = get_slugs()
    except Exception as e:
        return Response(json.dumps({'error': str(e)}, indent=4), mimetype='application/json')
    json_response = {}
    for slug in all_data:
        response = requests.post(url='https://api.alphabot.app/v1/register', headers={'Authorization': f'Bearer {API_KEY}'}, data={'slug': slug})
        if response.json()['success'] == True:
            logging.info(f'Successfully registered for {slug}')
            json_response[slug] = 'Success'
        else:
            if 'resultMd' in response.json():
                logging.error(f'Failed to register for {slug} -- Reason:'+response.json()['data']['resultMd']) 
                json_response[slug] = response.json()['data']['resultMd']+ ' Link: https://alphabot.app/'+slug
            else:
                try:
                    logging.error(f'Failed to register for {slug} -- Reason:'+response.json()['errors'][0]['message'] )
                except:
                    logging.error(f'Failed to register for {slug} -- Reason: Unknown')
                json_response[slug] = response.json()['errors'][0]['message'] + ' Link: https://alphabot.app/'+slug
    return Response(json.dumps(json_response, indent=4), mimetype='application/json')
        


if __name__ == '__main__':
    app.run()