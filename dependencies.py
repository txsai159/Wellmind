from flask import Flask, request, jsonify
from werkzeug.utils import safe_join

from flask_cors import CORS
from flask_debug import Debug
from pymongo import MongoClient
from datetime import date
import bcrypt
import jwt
import datetime
import re
import uuid
import os,sys
from database import mongo   
import random
import string
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import timedelta
import requests
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_mail import Mail, Message
# from flask_jwt_extended import (JWTManager, jwt_required, get_jwt_identity,  create_access_token, create_refresh_token, jwt_refresh_token_required, get_raw_jwt)


from flask import Flask, url_for, session, request, jsonify, make_response, send_from_directory, Blueprint, render_template, Response,send_file
#https://towardsdatascience.com/a-python-api-for-background-requests-based-on-flask-and-multi-processing-187d0e3049c9
from bson.objectid import ObjectId
from bson import json_util
import datetime,  json, os, sys
from threading import Thread
from flask_pymongo import PyMongo
from datetime import date
from bson import json_util

############################# mongodb service functions #######################
def check_the_status_mongodb_service():
    mongodb_r_status_filename = 'mongodb_rtatusoutput.txt'
    try:
        result = os.system('service mongod status > '+mongodb_r_status_filename)
        if result == 0:
            if os.path.exists(mongodb_r_status_filename):
                fp = open(mongodb_r_status_filename, "r")
                output = fp.read()
                fp.close()
                os.remove(mongodb_r_status_filename)
                if "Active: active (running)" in output :
                    return True
                else:
                    return False
            else:
                return False
        else:
            result1 = os.system('service mongodb status > '+mongodb_r_status_filename)
            if result1 == 0:
                if os.path.exists(mongodb_r_status_filename):
                    fp = open(mongodb_r_status_filename, "r")
                    output = fp.read()
                    fp.close()
                    os.remove(mongodb_r_status_filename)
                    if "Active: active (running)" in output :
                        return True
                    else:
                        return False
                else:
                    return False
            return False
    except Exception as error:
        
        return False
    


def restart_mongodb_r_service():
    try:
        if check_the_status_mongodb_service():
            return True
            
        else:
            result = os.system('echo "docketrun" | sudo -S service mongod restart')
            if result == 0:
                if check_the_status_mongodb_service():
                    return True
                else:
                    return False
            else:
                result1 = os.system('echo "docketrun" | sudo -S service mongodb restart')
                if result1== 0:
                    if check_the_status_mongodb_service():
                        return True
                    else:
                        return False
                else:
                    return False
            
    except Exception as error:
         
        return False
    

def forcerestart_mongodb_r_service():
    try:
        result = os.system('echo "docketrun" | sudo -S service mongod restart')
        if result == 0:
            if check_the_status_mongodb_service():
                return True
            else:
                return False
        else:
            result1 = os.system('echo "docketrun" | sudo -S service mongodb restart')
            if result1== 0:
                if check_the_status_mongodb_service():
                    return True
                else:
                    return False
            else:
                return False            
    except Exception as error:
        
        return False
    
def start_mongodb_r_service():
    try:
        result = os.system('echo "docketrun" | sudo -S service mongod start ')
        if result == 0:
            if check_the_status_mongodb_service():
                return True
            else:
                return False
        else:
            result = os.system('echo "docketrun" | sudo -S service mongodb start ')
            if result == 0:
                if check_the_status_mongodb_service():
                    return True
                else:
                    return False
            else:
                return False
    except Exception as error:
        
        return False
    

def stop_mongodb_service():
    try:#sudo service mongod stop
        result = os.system('echo "docketrun" | sudo -S service mongod stop')
        if result == 0:
            if check_the_status_mongodb_service():
                return True
            else:
                return False
        else:
            result1 = os.system('echo "docketrun" | sudo -S service mongodb stop')
            if result1 == 0:
                if check_the_status_mongodb_service():
                    return True
                else:
                    return False
            else:
                return False
    except Exception as error:
               
        return False
    
def enable_mongodb_r_service_to_system():
    mongodb_r_status_filename = 'mongodb_rtatusenableoutput.txt'
    try:
        result = os.system('echo "docketrun" | sudo -S service mongod enable  > '+mongodb_r_status_filename)
        if result == 0:
            if os.path.exists(mongodb_r_status_filename):
                fp = open(mongodb_r_status_filename, "r")
                output = fp.read()
                fp.close()
                os.remove(mongodb_r_status_filename)
                return True
            else:
                return False
        else:
            result = os.system('echo "docketrun" | sudo -S service mongodb enable  > '+mongodb_r_status_filename)
            if result == 0:
                if os.path.exists(mongodb_r_status_filename):
                    fp = open(mongodb_r_status_filename, "r")
                    output = fp.read()
                    fp.close()
                    os.remove(mongodb_r_status_filename)
                    return True
                else:
                    return False
            else:
                return False
    except Exception as error:
           
        return False
    
def disable_mongodb_r_service_to_system():
    mongodb_r_status_filename = 'mongodb_rtatusdisableoutput.txt'
    try:
        result = os.system('echo "docketrun" | sudo -S service mongod disable  > '+mongodb_r_status_filename)
        if result == 0:
            if os.path.exists(mongodb_r_status_filename):
                fp = open(mongodb_r_status_filename, "r")
                output = fp.read()
                fp.close()
                os.remove(mongodb_r_status_filename)
                return True
            else:
                return False
        else:
            return False
    except Exception as error:
            
        return False
    


def check_the_mongodb_r_installed_version():
    mongodb_rversion_file = "mongodb_rversion.txt"
    try:
        result = os.system('mongod --version> '+mongodb_rversion_file)#('echo "docketrun" | sudo -S service mongod disable  > '+mongodb_rversion_file)
        if result == 0:
            if os.path.exists(mongodb_rversion_file):
                fp = open(mongodb_rversion_file, "r")
                output = fp.read()
                fp.close()
                os.remove(mongodb_rversion_file)
                return True
            else:
                return False
        else:
            result2 = os.system('mongod -V> '+mongodb_rversion_file)
            if result2 ==0:
                if os.path.exists(mongodb_rversion_file):
                    fp = open(mongodb_rversion_file, "r")
                    output = fp.read()
                    fp.close()
                    os.remove(mongodb_rversion_file)
                    return True
                else:

                    return False
            else:
                result2 = os.system('mongodb --version > '+mongodb_rversion_file)
                if result2 ==0:
                    if os.path.exists(mongodb_rversion_file):
                        fp = open(mongodb_rversion_file, "r")
                        output = fp.read()
                        fp.close()
                        os.remove(mongodb_rversion_file)
                        return True
                    else:

                        return False
                else:
                    result3 = os.system('mongodb -V> '+mongodb_rversion_file)
                    if result3 ==0:
                        if os.path.exists(mongodb_rversion_file):
                            fp = open(mongodb_rversion_file, "r")
                            output = fp.read()
                            fp.close()
                            os.remove(mongodb_rversion_file)
                            return True
                        else:
                            return False
                    else:
                        return False
    except Exception as error:
        return False
   

#################################ALPHANUMERIC TOKEN GENERATION FUNCTIONS #############
def genarate_alphanumeric_key():
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for i in range(200))
    return key


def genarate_alphanumeric_key_for_riro_data():
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for i in range(25))
    return key


def GENERATEALPHANUMERICKEYFOREXCELTEST50():
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for i in range(50))
    return key

############################ dict and json #############################
def read_json_for_roi(json_fileName):
    with open(json_fileName, 'r') as f:
        data = json.load(f)
    return data

def parse_json(data):
    return json.loads(json_util.dumps(data))


def parse_json_dictionary(data):
    return json_util.dumps(data)


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def isEmpty(dictionary):
    for element in dictionary:
        if element:
            return True
        return False
    
def check_dictionaryishavinganynonevalue(dictionary):
    dictionary_status = True
    for element in dictionary:
        if element is None or element ==' ':
            dictionary_status= True
    return dictionary_status

def check_arraydictionaryishavinganynonevalue(dictionary):
    dictionary_status = True
    for dic in dictionary:
        if any([v==None for v in dic.values()]):
            dictionary_status= False
            break
    return dictionary_status

def delete_keys_from_dict(dictionary, keys):
    keys_set = set(keys)
    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            else:
                modified_dict[key] = value
    return modified_dict

def delete_keys_from_list_of_dict_multi_isolation(list_of_dict, keys):
    keys_set = set(keys)
    modified_dict = {}
    if type(list_of_dict) == list:
        for mirror in list_of_dict:
            dictionary = mirror
            for key, value in dictionary.items():
                if key not in keys_set:
                    if isinstance(value, MutableMapping):
                        modified_dict[key] = delete_keys_from_dict(value, keys_set)
                    else:
                        modified_dict[key] = value
    elif type(list_of_dict) == dict:
        dictionary = list_of_dict 
        for key, value in dictionary.items():
            if key not in keys_set:
                if isinstance(value, MutableMapping):
                    modified_dict[key] = delete_keys_from_dict(value, keys_set)
                else:
                    modified_dict[key] = value
    return modified_dict


def dictionary_key_exists(dictionary,key):
    if key in dictionary.keys():
        return True
    else:
        return False

############################ relative path functions ###################
def get_current_dir_and_goto_parent_dir():
    return os.path.dirname(os.getcwd())


def parent_directory_grandpa_dir():
    relative_parent = os.path.join(os.getcwd(), "../..") 
    return os.path.abspath(relative_parent)


##################CREAT FOLDER AND FILES #################
def create_multiple_dir(path):
    os.makedirs(path, exist_ok=True)

def handle_uploaded_file(target_dir):
    os.umask(0)
    os.makedirs(target_dir, mode=511, exist_ok=True)


def try_chmod_command(file):
    os.chmod(file, 511)




################### Date time FUNCTION #################
def testing_today_date():
    today_date = str(datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d'))
    return today_date

def now_time():
    return datetime.datetime.now().replace(second=0, microsecond=0)


def now_time_with_time():
    now = str(datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
    return now



def only_date():
    now = str(datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d'))
    return now


def now_time_with_time_minus():
    from datetime import datetime, timedelta
    now = str(datetime.strptime((datetime.now() - timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
    return now


def get_time_in_seconds(cutime, dbtime):
    hour_seconds = cutime.split(' ')[1]
    hour_seconds = hour_seconds.strip()
    chr, cmin, csec = hour_seconds.split(':')
    current_in_seconds = int(int(chr) * 60 * 60) + int(int(cmin) * 60) + int(int(csec))
    db_hour_seconds = dbtime.split(' ')[1]
    db_hour_seconds = db_hour_seconds.strip()
    db_hr, db_min, db_sec = db_hour_seconds.split(':')
    db_in_seconds = int(int(db_hr) * 60 * 60) + int(int(db_min) * 60) + int(int(db_sec))
    return current_in_seconds - db_in_seconds




############################---- system and process related function ---############################## 
    
def remove_empty_elements_from_list(split_data):
    while '' in split_data:
        split_data.remove('')
    return split_data
    

##########list of dictionary and keys checking
def check_the_data_keys(key_in_riro_data, dataKeys):
    similar_keys = [i for i in list(dataKeys) if i in key_in_riro_data]
    check_dict_status = all(x in key_in_riro_data for x in list(dataKeys))
    return check_dict_status

def remove_duplicate_elements_from_two_list(first_list, second_list):
    in_first = set(first_list)
    in_second = set(second_list)
    in_second_but_not_in_first = in_second - in_first
    result = first_list + list(in_second_but_not_in_first)
    return result

def empty_list_function(list1):
    list2 = [x for x in list1 if x != []]
    return list2

    
##################### pagination functions ######################

######################################### STRING FUNCTIONS ##########################################
try:
    def remove_underscore(state_name):
        if state_name is not None:
            final_string = state_name.replace('_', ' ')
            return final_string
        else:
            return None
except Exception as error:
    
    print(str(error))

try:
    def replace_spl_char(string):
        not_require =[":","-","."," "] #[':', '-', '.', ' ']
        for i in not_require:
            if i in string:
                string = string.replace(i, '_')
        return string
except Exception as error:
    
    print(str(error))

try:
    def remove_all_specail_char_with_hifhen(test_string):
        special=[';', ':', '!', "*",'@','#','&','%',' ',] 
        for i in special :
            test_string = test_string.replace(i,'-') 
        return test_string
except  Exception as error :
    print('error  removing the special character---')


def replace_spl_char_panel_area_plant(string):
    not_require = [':', '.', ' ']
    for i in not_require:
        if i in string:
            string = string.replace(i, '-')
    return string


def replace_spl_char_time_to(string):
    not_require = [':', '.', ' ']
    for i in not_require:
        if i in string:
            string = string.replace(i, '-')
    return string

try:
    def remove_space_character(state_name):
        if state_name is not None:
            final_string = state_name.replace(' ', '-')
            return final_string
        else:
            return None
except Exception as error:
    
    print(str(error))

try:
    def remove_ampercent(state_name):
        if state_name is not None:
            final_string = state_name.replace('&', '-')
            return final_string
        else:
            return None
except Exception as error:
    
    print(str(error))


def clean(txt):
    try:
        txt.replace('Â', '')
    except:
        txt = txt
    return txt

def clear_asci(myString):
    return myString.replace('\xa0', '')

#######################################################################################
def split_for_bbox_points(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


def time_sort_key(d):
    return d['irrd_in_time']


def job_sheet_time_sort_key(d):
    # print("JOBSHEETWISE ------------------------------------------------------------", d)
    return d['sort_id']#d['job_sheet_time']


def sort_irrd_time_(time_stamp_data):
    final_time_sort = sorted(time_stamp_data, key=time_sort_key, reverse=True)
    return final_time_sort


def sort_job_sheet_time_sort_key_(mongo_id_data):    
    final_time_sort = sorted(mongo_id_data, key=job_sheet_time_sort_key,reverse=True)
    return final_time_sort