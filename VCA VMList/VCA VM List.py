# coding=utf-8
import requests
import getpass
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import csv
import os
API_URL = input("Enter the vca url > Ondemand url/vCloud Director API url: ")
if 'orgName' in API_URL:
    ORGNAME = ((API_URL.split('='))[1].split('&'))[0]
    if ORGNAME=='true':
        ORGNAME=((API_URL.split('='))[2].split('&'))[0]
    API_URL = 'https://' + (API_URL.split('/'))[2] + '/api/compute/api'
else:
    ORGNAME = (API_URL.split('/'))[-2];API_URL = 'https:' + (API_URL.split(':'))[1] + '/api'
USERNAME =input("Username: ")
USERNAME=USERNAME+'@'+ORGNAME
PASSWORD =getpass.getpass('Password:')
class Cloud():
    def __init__(self, api_url, username=None, password=None):
        self.token = None
        self.headers = {'accept':'application/*+xml;version=5.7'}
        self._api_url = api_url
        self._username = username
        self._password = password
    def login(self):
        username = self._username or input('Username: ')
        password = self._password or getpass.getpass(prompt='Password: ')
        api_url = self._api_url+'/sessions'
        r = requests.post(api_url, auth=HTTPBasicAuth(username, password),headers=self.headers, proxies=None)
        self.token = r.headers.get('x-vcloud-authorization')
        self.headers['x-vcloud-authorization'] = self.token
    def query_vm_url(self):
        print( 'Querying VMs')
        page=1;vmlist={};rel="nextPage";gotonextpage=1;b=1
        while(gotonextpage==1):
            gotonextpage = 0
            response = self.run_vm_query(page)
            xml_tree = ET.fromstring(response)
            for item in xml_tree:
                if (item.get('catalogName'))==None and (item.get('name')!=None):
                    vmname = item.get( 'name' );vapp = item.get( 'containerName');IPAddress = item.get( 'ipAddress' );guestOs=item.get( 'guestOs' );memoryMB = item.get( 'memoryMB' );networkName = item.get( 'networkName' );numberOfCpus = item.get( 'numberOfCpus' );status = item.get( 'status' )
                    vmlist[b]={};vmlist[b]['vmname']=vmname;vmlist[b]['vApp']=vapp;vmlist[b]['IPAddress'] = IPAddress;vmlist[b]['guestOs']=guestOs;vmlist[b]['memoryMB'] = memoryMB;vmlist[b]['networkName'] = networkName;vmlist[b]['numberOfCpus'] = numberOfCpus;vmlist[b]['status'] = status;b+=1
                if rel == item.get('rel'):
                    gotonextpage=1;page+=1
        return vmlist
    def run_vm_query(self,page):
        query_url = self._api_url + '/query?type=vm&pageSize=1024&page='+str(page)
        response1 = requests.get( query_url, headers=self.headers)
        response = response1.content
        return response
def main():
    vca = Cloud(API_URL, username=USERNAME, password=PASSWORD)
    vca.login()
    vmlist= vca.query_vm_url()
    with open( 'names.csv', 'w', newline='' ) as csvfile:
        fieldnames = ['vmname', 'vApp', 'IPAddress', 'networkName', 'memoryMB', 'numberOfCpus', 'status', 'guestOs'];n=1
        writer = csv.DictWriter( csvfile, fieldnames=fieldnames )
        writer.writeheader()
        while n <= len( vmlist.keys() ):
            writer.writerow( vmlist[n] )
            n = n + 1
    print( 'No of vms:', len( vmlist.keys() ) )
    currentPath = os.getcwd()
    filepath=currentPath + "/Names.csv"
    print('File Location: ',filepath)
    excel=r'"C:\Program Files (x86)\Microsoft Office\root\Office16\excel.exe" names.csv'
    os.system(excel)
if __name__ == '__main__':
    main()
