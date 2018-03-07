# coding=utf-8
import requests
import getpass
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


API_URL = input("Enter the vca url(Ondemand url/vCloud Director API url): ")

if 'orgName' in API_URL:
    ORGNAME = ((API_URL.split( '=' ))[1].split( '&' ))[0]
    API_URL='https://'+(API_URL.split('/'))[2]+'/api/compute/api'
    ENVIRONMENT='OnDemand'
else:
    ORGNAME = (API_URL.split( '/' ))[-2]
    API_URL = 'https:' + (API_URL.split( ':' ))[1] + '/api'
    ENVIRONMENT='VPC'
    EDGE_NAME = input( 'Gateway name:' )  # 'gateway' #Edge Gateway Name

USERNAME = 'francisa@vmware.com' #input('Enter username:') #
USERNAME=USERNAME+'@'+ORGNAME
PASSWORD = 'Jan@2011' #input('Enter password:')# #Password


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
        print('Logging in to [%s]...' % api_url)
        r = requests.post(api_url, auth=HTTPBasicAuth(username, password),
                          headers=self.headers, proxies=None)
        print('Status:', r.status_code, r.reason)
        self.token = r.headers.get('x-vcloud-authorization')
        self.headers['x-vcloud-authorization'] = self.token
        print('headers::',self.headers)
        print('Auth Token::', self.token)

    def query_edge_url(self, name):
        print( 'Querying edges for {}'.format( name ) )
        params = {'type': 'edgeGateway', 'format': 'references'}
        response = self.run_query( params )
        xml_tree = ET.fromstring( response )
        print( 'xml_tree:', xml_tree )
        for item in xml_tree:
            if item.get( 'name' ) == name:
                return item.get( 'href' )

    def run_query(self, query_parameters):
        query_url = self._api_url + '/query'
        print( 'query_url::', query_url )
        response1 = requests.get( query_url, headers=self.headers, params=query_parameters )
        print( 'response1::', response1 )
        response = response1.content
        return response

    def OD_query_vdc_url(self):
        print( 'Querying org')
        params = {'type': 'orgVdc', 'format': 'references'}
        response = self.OD_run_vdc_query( params )
        xml_tree = ET.fromstring(response)
        vdcname=[];herf=[]
        for item in xml_tree:
            abc=item.get( 'name' )
            if abc!=None:
                vdcname.append(abc)
                abc2 = item.get( 'href' )
                herf.append(abc2)
        print("vdcname::",vdcname)
        vdc_herf=dict(zip(vdcname,herf))
        customer_org = input( 'Enter vdc name: ' )
        print('You have selected:',customer_org)
        return vdc_herf[customer_org]

    def OD_run_vdc_query(self, query_parameters):
        query_url = self._api_url + '/query'
        response1 = requests.get( query_url, headers=self.headers, params=query_parameters )
        response = response1.content
        return response

    def OD_query_edge_url(self, vdc_url):
        response = self.OD_run_edge_query( vdc_url )
        xml_tree = ET.fromstring( response )
        for item in xml_tree:
            if item.get( 'rel' )=="edgeGateways":
                return item.get( 'href' )

    def OD_run_edge_query(self, vdc_url):
        response2 = requests.get( vdc_url, headers=self.headers)
        response = response2.content
        return response

    def OD_query_edge_id_url(self, edge_url):
        response = self.OD_run_edge_id_query( edge_url )
        xml_tree = ET.fromstring( response )
        for item in xml_tree:
            if item.get( 'name' )=="gateway":
                return item.get( 'href' )

    def OD_run_edge_id_query(self, edge_url):
        response3 = requests.get( edge_url, headers=self.headers)
        response = response3.content
        return response

class Gatewayredeploy():

    def __init__(self, edge_url, auth_token):
        self.edge_url = edge_url
        self.api_endpoint = '/action/redeploy'
        self.headers = {'accept':'application/*+xml;version=5.6','x-vcloud-authorization':auth_token}

    def submit_changes(self):
        submit_url = str(self.edge_url) + self.api_endpoint
        result = requests.post(submit_url, headers=self.headers)
        print('API Endpoint: ', result.request.url)
        print('Status: {} {}'.format(result.status_code, result.reason))

def main():
    vca = Cloud(API_URL, username=USERNAME, password=PASSWORD)
    vca.login()
    if ENVIRONMENT=='VPC':
        edge_url = vca.query_edge_url(EDGE_NAME)
        print("edge_url:",edge_url)
        redeploy=Gatewayredeploy(edge_url,vca.token)
        redeploy.submit_changes()

    elif ENVIRONMENT == 'OnDemand':
        vdc_url = vca.OD_query_vdc_url()
        edge_url = vca.OD_query_edge_url( vdc_url )
        edge_id_url = vca.OD_query_edge_id_url( edge_url )
        redeploy = Gatewayredeploy( edge_id_url, vca.token )
        redeploy.submit_changes()

if __name__ == '__main__':
    main()
