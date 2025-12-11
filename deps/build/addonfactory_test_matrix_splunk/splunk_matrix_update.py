import requests
import re
import configparser
import json
import os
from packaging import version

def get_token():
    splunk_token_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:splunk/splunk:pull"
    response = requests.get(splunk_token_url)
    response_json = json.loads(response.text)
    token = response_json['token']
    return token

def get_images_list(token):
    headers = {'Authorization':'Bearer {}'.format(token)}
    splunk_image_list_url = "https://registry.hub.docker.com/v2/splunk/splunk/tags/list"
    response = requests.get(splunk_image_list_url,headers = headers)
    response_json = json.loads(response.text)
    return response_json['tags']

def get_latest_image(stanza,images):
    stanza = stanza.split('.')
    stanza = '\.'.join(stanza)
    regex_image = r"'{}\.\d+'|'{}\.\d+\.\d+'".format(stanza,stanza)
    filtered_images = re.findall(regex_image,str(images))
    if filtered_images:
        for i in range(len(filtered_images)):
            filtered_images[i] = filtered_images[i].replace('\'','')
        filtered_images.sort(key=lambda s: list(map(int, s.split('.'))))
        return filtered_images[-1]

def check_image_version(latest_image,stanza_image):
    if version.parse(latest_image) > version.parse(stanza_image):
        return True
    else:
        return False

def filter_image_list(images_list):
    regex_filter_images = r"\'[0-9a-z]{12}\'"
    filter_images = re.findall(regex_filter_images,str(images_list))
    if filter_images:
        for i in range(len(filter_images)):
            filter_images[i] = filter_images[i].replace('\'','')
        return filter_images

def get_image_digest(token,image):
    headers = {'Authorization':'Bearer {}'.format(token),'Accept':'application/vnd.docker.distribution.manifest.v2+json'}
    image_digest_url = "https://registry.hub.docker.com/v2/splunk/splunk/manifests/{}".format(image)
    response = requests.get(image_digest_url,headers = headers)
    if response.headers['Docker-Content-Digest']:
        return response.headers['Docker-Content-Digest']
    else:
        token = get_token()
        headers = {'Authorization':'Bearer {}'.format(token),'Accept':'application/vnd.docker.distribution.manifest.v2+json'}
        image_digest_url = "https://registry.hub.docker.com/v2/splunk/splunk/manifests/{}".format(image)
        response = requests.get(image_digest_url,headers = headers)
        return response.headers['Docker-Content-Digest']

def get_build_number(token,filter_images,latest_image_digest):
    for image in filter_images:
        if get_image_digest(token,image) == latest_image_digest:
            return image

def update_splunk_version(token):
    if os.path.isfile('splunk_matrix.conf'):
        config = configparser.ConfigParser()
        config.optionxform=str
        config.read('splunk_matrix.conf')
        update_file = False
        images_list = get_images_list(token)
        filter_images = filter_image_list(images_list)
        for stanza in config.sections():
            latest_image_version = get_latest_image(stanza,images_list)
            stanza_image_version = config.get(stanza,'VERSION')
            
            if check_image_version(latest_image_version,stanza_image_version):
                config.set(stanza,'VERSION',latest_image_version)
                latest_image_digest = get_image_digest(token,latest_image_version)
                build_number = get_build_number(token,filter_images,latest_image_digest)
                config.set(stanza,'BUILD',build_number)
                update_file = True
        
        if update_file:
            with open('splunk_matrix.conf','w') as configfile:
                config.write(configfile)
            return "True"
    return "False"

if __name__ == '__main__':
    token = get_token()
    update_file = update_splunk_version(token)
    print(update_file)
