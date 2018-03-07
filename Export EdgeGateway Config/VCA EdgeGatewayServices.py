"""
Description : Exports the vCloud Air EdgeGateway configurations like NAT, Firewall, Loadbalancer, IPSecvpnservice, SSLvpnservice, Networks, DHCPservice, Routing to jason file
Scope       : Applicable to VPC, OnDemand & DR vCloud Air environment
Execution   : Run this script from cmd prompt and provide the required inputs
Inputs      : OnDemand > OnDemand URL, VPC > vCloud Director API URL
            : vCloud Air credentials
            : gateway name(vpc)
            : vdc name sl no(ondemand)

Output      : Output file is json, use notpad++ for a formatted view

Complete list ip address can be found under "ipList"
Use below keywords to search in output file. No results in keyword search if services are not configured.
NatService
IpsecVpnService
FirewallService
LoadBalancerService
StaticRoutingService

Prerequisite: Install python3.0 or higher
            : Install requests module as it is not a builtin module(From a cmd prompt, use > Path\easy_install.exe requests, where Path is your Python*\Scripts folder, if it was installed. (For example: C:\Python32\Scripts\easy_install.exe))

Queries     : Contact me on abin.francis@corp.ovh.us or abin001@gmail.com for any queries

"""

import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import json
import os
import getpass
print( '\n' )
API_URL = input("Enter the vca url(Ondemand url/vCloud Director API url): ")

if 'orgName' in API_URL:
    ORGNAME = ((API_URL.split( '=' ))[1].split( '&' ))[0]
    if ORGNAME=='true':
        ORGNAME=((API_URL.split('='))[2].split('&'))[0]
    API_URL='https://'+(API_URL.split('/'))[2]+'/api/compute/api'
    ENVIRONMENT='OnDemand'
else:
    ORGNAME = (API_URL.split( '/' ))[-2]
    API_URL = 'https:' + (API_URL.split( ':' ))[1] + '/api'
    ENVIRONMENT='VPC';print('\n')
    print('-'*30)
    print('Enter EdgeGateway display name');print( '-' * 30,'\n' )
    EDGE_NAME = input( 'Gateway name:' );print( '\n' )
print( '\n' )
USERNAME = input('Enter username:') #
USERNAME=USERNAME+'@'+ORGNAME
PASSWORD = getpass.getpass('Password:')

class Cloud():
    def __init__(self, api_url, username=None, password=None):
        self.token = None
        self.headers = {'accept':'application/*+xml;version=5.7'}
        self._api_url = api_url
        self._username = username
        self._password = password
    def login(self):
        username = self._username
        password = self._password or getpass.getpass(prompt='Password: ')
        api_url = self._api_url+'/sessions'
        r = requests.post(api_url, auth=HTTPBasicAuth(username, password),
                          headers=self.headers, proxies=None)
        self.token = r.headers.get('x-vcloud-authorization')
        self.headers['x-vcloud-authorization'] = self.token
    def query_edge_url(self, name):
        params = {'type': 'edgeGateway', 'format': 'references'}
        response = self.run_query( params )
        xml_tree = ET.fromstring( response.content )
        for item in xml_tree:
            if item.get( 'name' ) == name:
                return item.get( 'href' )
    def run_query(self, query_parameters):
        query_url = self._api_url + '/query'
        return requests.get( query_url, headers=self.headers, params=query_parameters )

    def edge_config_url(self, edge_url):
        response = self.run_edge_config_url( edge_url )
        configdict=json.loads(response.content)
        with open( "EdgeGatewayervices.json", "w" ) as f:
            f.write( json.dumps( configdict,indent=4 ))

    def run_edge_config_url(self, edge_url):
        edgeconfig_url=edge_url+'/exportConfig'
        return requests.get( edgeconfig_url, headers=self.headers)

    def OD_query_vdc_url(self):
        params = {'type': 'orgVdc', 'format': 'references'}
        response = self.OD_run_vdc_query( params )
        xml_tree = ET.fromstring(response.content)
        vdcname=[];herf=[]
        for item in xml_tree:
            abc=item.get( 'name' )
            if abc!=None:
                vdcname.append(abc)
                abc2 = item.get( 'href' )
                herf.append(abc2)
        print('\n'*2)
        print('-'*57)
        print("Enter VDC's sl no. from below list")
        print('-'*57)
        no=1
        for x in vdcname:
            print(no,'. ',x)
            no+=1
        print( '-' * 57)
        print( '\n')
        vdc_herf=dict(zip(vdcname,herf))
        customer_org = int(input( 'Enter vdc number: ' ))
        print('Selected VDC: ',vdcname[(customer_org)-1])
        return vdc_herf[vdcname[(customer_org)-1]]
    def OD_run_vdc_query(self, query_parameters):
        query_url = self._api_url + '/query'
        return requests.get( query_url, headers=self.headers, params=query_parameters )
    def OD_query_edge_url(self, vdc_url):
        response = self.OD_run_edge_query( vdc_url )
        xml_tree = ET.fromstring( response.content )
        for item in xml_tree:
            if item.get( 'rel' )=="edgeGateways":
                return item.get( 'href' )
    def OD_run_edge_query(self, vdc_url):
        return requests.get( vdc_url, headers=self.headers)
    def OD_query_edge_id_url(self, edge_url):
        response = self.OD_run_edge_id_query( edge_url )
        xml_tree = ET.fromstring( response.content )
        for item in xml_tree:
            if item.get( 'name' )=="gateway":
                return item.get( 'href' )
    def OD_run_edge_id_query(self, edge_url):
        return requests.get( edge_url, headers=self.headers)
def main():
    vca = Cloud(API_URL, username=USERNAME, password=PASSWORD)
    vca.login()
    if ENVIRONMENT=='VPC':
        edge_url = vca.query_edge_url(EDGE_NAME)
        print( 'Exporting gatway configuration...' )
        vca.edge_config_url(edge_url)

    elif ENVIRONMENT == 'OnDemand':
        vdc_url = vca.OD_query_vdc_url()
        edge_url = vca.OD_query_edge_url( vdc_url )
        edge_id_url = vca.OD_query_edge_id_url(edge_url)
        print( 'Exporting gatway configuration...' )
        vca.edge_config_url(edge_id_url)

    currentPath = os.getcwd()
    filepath = currentPath + "\EdgeGatewayervices.json"
    print( '-' * (len(list(filepath))+16) )
    print( 'File Location: ', filepath )
    print( '-' * (len( list( filepath ) ) + 16) )
    notepad = (r'"C:\Program Files (x86)\Notepad++\notepad++.exe" EdgeGatewayervices.json')
    os.system( notepad )
    exit()
if __name__ == '__main__':
    main()
