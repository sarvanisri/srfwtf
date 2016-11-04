#!/usr/bin/env python
'''
Created on 3-Nov-2016

Author : Terralogic team

OpenSnaprouteCliDriver is the basic driver which will handle the OpenSnaproute functions.

'''
import io
import sys
import os
import simplejson as json
sys.path.append(os.path.abspath('../../py'))
from flexswitchV2 import FlexSwitch
from flexprintV2 import FlexSwitchShow



import xmldict
import pexpect
import re
import os
import ast
import time
import testfail 
import string
import sys
import logger as log
from robot.libraries.BuiltIn import BuiltIn
global step



'''
[API Documentation]
#ID : ops_api_001
#Name :  Connect API
#API Feature details :
#1 "Connect" API Connects to the particular device.
'''

def Connect(device):
    device_name=Device_parser(device)
    device_Info=Get_deviceInfo(device_name)
    ip_address=device_Info[1]
    user=device_Info[2]
    password=device_Info[3]
    refused="ssh: connect to host " +ip_address+ " port 22: Connection refused"
    connectionInfo = pexpect.spawn('ssh '+user+'@'+ip_address )
    expect = 7
    while expect == 7:
        expect =connectionInfo.expect( ["Are you sure you want to continue connecting","password:",pexpect.EOF,pexpect.TIMEOUT,refused,'>|#|\$',"Host key verification failed."],120 )  
        if expect == 0:  # Accept key, then expect either a password prompt or access
            connectionInfo.sendline( 'yes' )
            expect = 7  # Run the loop again
            continue
        if expect == 1:  # Password required  
            connectionInfo.sendline(password)
            connectionInfo.expect( '>|#|\$')
            if not connectionInfo.expect:
                log.failure('Password for '+device_name+' is incorrect')
                raise testfail.testFailed('Password for '+device_name+' is incorrect')
                break
        elif expect == 2:
            log.failure('End of File Encountered while Connecting '+device_name)
            raise testfail.testFailed('End of File Encountered while Connecting '+device_name)
            break
        elif expect == 3:  # timeout
            log.failure('Timeout of the session encountered while connecting')
            raise testfail.testFailed('Timeout of the session encountered')
            break
        elif expect == 4:
            log.failure('Connection to '+device_name+' refused')
            raise testfail.testFailed('Connection to '+device_name+' refused')
            break
        elif expect == 5:
            pass
        elif expect == 6:
            cmd='ssh-keygen -R ['+ip_address+']:'+port
            os.system(cmd)
            connectionInfo = pexpect.spawn('ssh -p '+port +' ' +user+'@'+ip_address,env={ "TERM": "xterm-mono" },maxread=50000 )
            expect = 7
            continue
    connectionInfo.sendline("")
    connectionInfo.expect( '>|#|\$' )
    return connectionInfo
    



def curl_connect(device) :
    device_name=Device_parser(device)
    device_Info = Get_deviceInfo(device_name)
    ip_address = device_Info[1]
    swtch = FlexSwitch (ip_address, 8080)  # Instantiate object to talk to flexSwitch
    show =FlexSwitchShow (ip_address, 8080)
    return swtch
    #CREATED(FAILED)
    #print json.dumps(createBGPv4_Neighbor)


'''
[API Documentation]
#ID : ops_api_002
#Name :  Deviceparser API
#API Feature details :
#1  "Deviceparser" API Parses the "TestCase.params" file
#2  Returns the device name                                     
'''

def Device_parser(device="") :
    xml = open('OpenSnaproute.params').read()
    parsedInfo = xmldict.xml_to_dict(xml)
    if device!="":
        device=str(device)
        device_name=parsedInfo['TestCase']['Device'][device]
        return device_name
    else:
        device_name=parsedInfo['TestCase']['Device']
        return device_name


'''
[API Documentation] 
#ID : ops_api_003
#Name : Get_deviceInfo API
#API Feature details :
#1  "Get_deviceInfo" API opens the "device.params" file
#2  Returns the information of the particular device in a list
'''

def Get_deviceInfo(device):
    deviceparam=open('device.params').read()
    deviceInfo=deviceparam.splitlines() 
    for value in deviceInfo:
        pattern=device
        match=re.search(pattern,value)
        if match:          
            deviceList=value.split(',')
            return deviceList



def CHECKPOINT(string,device_id=''):
    log.step("*** "+string)

def CASE(string,device_id=''):
    log.case("<<< "+string)




'''
[API Documentation]
#ID : ops_api_0018
#Name : delay(delay,message)
#API Feature details :
#1 "delay" API makes the process wait for the Specified time.
'''

'''
delay  15  please wait for 60 seconds then check for BGP "state: Established"
'''
def delay(delay='',message=''):  
    if time!='':
        log.info(message)
        time.sleep(int(delay))
        return True
    else:
        return False
    






'''
[API Documentation] 
#ID : ops_api_0022
#Name : getTestCaseParams(testcase,test)
#API Feature details :
#1 API "getTestCaseParams" Parses the "OpenSnaproute.params" file.
#2 Returns the prarameters_details used in the testcase                             
'''

def getTestCaseParams(testcase="",test=""):
        testcase=str(testcase)
        if test=="":
                xml = open('OpenSnaproute.params').read()
                tc=xmldict.xml_to_dict(xml)
                testcaseInfo=tc['TestCase'][testcase]
                return testcaseInfo
        elif test!="":
                xml = open('OpenSnaproute.params').read()
                tc=xmldict.xml_to_dict(xml)
                test_values=tc['TestCase'][testcase][test]
                return test_values 





'''
[API Documentation]
#ID : ops_api_0024
#Name :parse_device(device) 
#API Feature details :
"parse_device" API opens and reads the PARAM(OpenSnaproute.params) File and Fetches and returns the Device information after converting into a Dictionary.
'''

def parse_device(device="") :
    xml = open('OpenSnaproute.params').read()
    parsedInfo = xmldict.xml_to_dict(xml)
    if device!="":
        device=str(device)
        device_name=parsedInfo['TestCase']['Device'][device]
        return device_name
    else:
        device_name=parsedInfo['TestCase']['Device']
        return device_name





def assignip(mode,fab_devices,csw_devices,asw_devices,subnet,fab=[],csw=[],asw=[],interface_dict={},interface_ip_dict={}) :
    list1=[]
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
        for i in range(len(list1)):
            port = []
            interface_ip=[]
            device = list1[i]
            device_name=Device_parser(device)
            log.info("login to "+device_name+" and configure IP address")
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            swtch = FlexSwitch (ip_address, 8080)  # Instantiate object to talk to flexSwitch
            for j in range(len(list1)):
                if device != list1[j] :
                    device_ip=device+"_"+list1[j]+"_interface_ip "
                    device_interface=device+"_"+list1[j]+"_eth"    
                    if device_ip in interface_ip_dict.keys() and device_interface in interface_dict.keys():
                        create_IPv4Intf=swtch.createIPv4Intf(interface_dict[device_interface],interface_ip_dict[device_ip]+subnet,AdminState='UP')
                        port.append(interface_dict[device_interface])
                        interface_ip.append(interface_ip_dict[device_ip]+subnet)
                        #print json.dumps(create_IPv4Intf)
            checkip(list1[i],port,interface_ip) 
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
        for i in range(len(list1)):
            port = []
            interface_ip=[]
            device = list1[i]
            device_name=Device_parser(device)
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            swtch = FlexSwitch (ip_address, 8080)  # Instantiate object to talk to flexSwitch
            for j in range(len(list1)):
                if device != list1[j] :
                    device_ip=device+"_"+list1[j]+"_interface_ip "
                    device_interface=device+"_"+list1[j]+"_eth"    
                    if device_ip in interface_ip_dict.keys() and device_interface in interface_dict.keys():
                        
                        create_IPv4Intf=swtch.createIPv4Intf(interface_dict[device_interface],interface_ip_dict[device_ip]+subnet,AdminState='UP')
                        port.append(interface_dict[device_interface])
                        interface_ip.append(interface_ip_dict[device_ip]+subnet)
                        #print json.dumps(create_IPv4Intf)
            checkip(list1[i],port,interface_ip)
                        #print json.dumps(create_IPv4Intf)
                                







def enablelldp(mode,fab_devices,csw_devices,asw_devices,fab=[],csw=[],asw=[]) :
    list1=[]
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
    for i in range(len(list1)) :
            device = list1[i]
            device_name=Device_parser(device)
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            swtch = FlexSwitch (ip_address, 8080)
            swtch.updateLLDPGlobal("default",Enable="True",TranmitInterval=30)
            showrun(list1[i],'LLDP','lldp enable')



def statedown(mode,fab_devices,csw_devices,asw_devices,fab=[],csw=[],asw=[],interface_dict={}) :
    list1=[]
    log.info("Making the interfaces state DOWN")
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
                       #print json.dumps(create_IPv4Intf)               
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
        
    for i in range(len(list1)):
            device = list1[i]
            device_name=Device_parser(device)
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            swtch = FlexSwitch (ip_address, 8080)  # Instantiate object to talk to flexSwitch
            for j in range(len(list1)):
                if device != list1[j] :
                    device_interface=device+"_"+list1[j]+"_eth"    
                    if device_interface in interface_dict.keys():
                        create_IPv4Intf=swtch.updatePort(interface_dict[device_interface],AdminState='DOWN')
                        
                        #print json.dumps(create_IPv4Intf)


def stateup(mode,fab_devices,csw_devices,asw_devices,fab=[],csw=[],asw=[],interface_dict={}) :
    list1=[]
    log.info("Making the interfaces state UP")
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
                        #print json.dumps(create_IPv4Intf)
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
        
    for i in range(len(list1)):
            port = []
            device = list1[i]
            device_name=Device_parser(device)
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            connectionInfo=Connect(device)
            connectionInfo.sendline("snap_cli")
            connectionInfo.expect(">")
            connectionInfo.sendline("enable")  
            connectionInfo.expect("#")
            connectionInfo.sendline("config")  
            connectionInfo.expect("#")
            for j in range(len(list1)):
                if device != list1[j] :
                    device_interface=device+"_"+list1[j]+"_eth"    
                    if device_interface in interface_dict.keys():
     
                        eth = interface_dict[device_interface]
                        port.append(eth)
                        eth = eth[:3] + ' ' + eth[3:]
                        connectionInfo.sendline("interface "+eth)  
                        connectionInfo.expect("#")
                        connectionInfo.sendline("no shutdown")  
                        connectionInfo.expect("#")          
                        connectionInfo.sendline("apply")  
                        connectionInfo.expect("#")
                        


'''
[API Documentation]
#ID : ops_api_0034
#Name : lldpNeighborInfo()
#API Feature details :
#1 " lldpNeighborInfo" API verifies the LLDP neighbour information.
'''



def lldpNeighborInfo(mode,fab_devices,csw_devices,asw_devices,devices=[],fab=[],csw=[],asw=[],interface_dict={}):

    Result=[]
    if mode == 'yes':
        for device in devices:
            device_name=Device_parser(device)
            device_Info = Get_deviceInfo(device_name)
            ip_address = device_Info[1]
            swtch = FlexSwitchShow (ip_address, 8080)
            test_name = BuiltIn().get_variable_value("${TEST_NAME}")      
            device_name=parse_device(device)
            device_params=getTestCaseParams(test_name,device_name)
            log.step('Checking LLDP Neighbor Information For The Device: '+device_name)
            lldp_dict = ast.literal_eval(device_params)
            result = swtch.printLLDPIntfStates()
            log.details(result)
            fd = open("sample.txt","w+")
            fd.write(result)
            fd.close()
            f = open("sample.txt","r")
            j=0
            count=0
            line = f.readlines()        
            for eachline in line :
                pattern1 = r'\s*([A-z0-9]*)\s*\d*\s*\d*\s*\d*\s*True\s*([A-z0-9]*)\s*[A-z0-9:]*\s*([A-z0-9]*)\s*([A-z0-9]*).*'
                match = re.match(pattern1,eachline)
                if match :
                    neighborportid = match.group(3) 
                    portid = match.group(1)
                    dest1 = match.group(4)
                    dest1 = dest1.lower()
                    for loop in range(len(lldp_dict)) :
                        source=lldp_dict[loop][j]
                        dest=lldp_dict[loop][j+1]
                        source_params=source.split(':')
                        dest_params=dest.split(':')
                        source_name=source_params[0]
                        source_port=source_params[1]
                        dest_name=dest_params[0]
                        dest_port=dest_params[1]
                        if source_port==portid and dest_port==neighborportid and dest_name == dest1: 
                            log.info("port "+portid+" of "+device_name+" Is Connected To Port "+neighborportid+" of "+dest1)
                            count=count+1
                            break
                            
#                    k=k+1
            os.remove("sample.txt")    
            if count==(len(lldp_dict)):
                log.success('LLDP Neighbor Information Matched With The Given Information\n')
                Result.append("Pass")
            else:
                log.failure('LLDP Neighbor Information Does Not Matches With The Given Information\n')
                Result.append("Fail") 
            count =0
            if "Fail" in Result:
                raise testfail.testFailed("LLDP neighbor information does not matches with the given information\n")
            

    if mode=='no':
        list1=[]
        list2=[]
        j=0
        rise=0
        count=0
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
        for i in range(0,len(list1)):
                device_n=list1[i]
                for device in list1:
                    if device != device_n :
                        device_interface=device_n+"_"+device+"_eth"    
                        if device_interface in interface_dict.keys():
                            list2.append(device)
                            rise=rise+1
                device_name=Device_parser(device_n)
                device_Info = Get_deviceInfo(device_name)
                ip_address = device_Info[1]
                swtch = FlexSwitchShow (ip_address, 8080)
                test_name = BuiltIn().get_variable_value("${TEST_NAME}")      
                device_name=parse_device(device_n)
                device_params=getTestCaseParams(test_name,device_name)
                log.step('Checking LLDP Neighbor Information For The Device: '+device_name)
                lldp_dict = ast.literal_eval(device_params)
                result = swtch.printLLDPIntfStates()          
                log.details(result)
                fd = open("sample.txt","w+")
                fd.write(result)
                fd.close()
                f = open("sample.txt","r")
                line = f.readlines()
#               for device in list2:
#                   j=0
#                   name=parse_device(device)
#                   name=name.lower()
                #print len(line)
                #print line
                #print list2
                for eachline in line :
                        
                        pattern1 = r'\s*([A-z0-9]*)\s*\d*\s*\d*\s*\d*\s*True\s*([A-z0-9]*)\s*[A-z0-9:]*\s*([A-z0-9]*)\s*([A-z0-9]*).*'
                        match = re.match(pattern1,eachline)
 
                        if match :
                            neighborportid = match.group(3) 
                            portid = match.group(1)
                            dest1 = match.group(4)
                            dest1 = dest1.lower()
                        for device in list2:
                          flag = 0
                          j=0
                          dest_n=parse_device(device)
                          dest_n=dest_n.lower()
                          if match:
                             for loop in range(len(lldp_dict)) :
                                source=lldp_dict[loop][j]
                                dest=lldp_dict[loop][j+1]
                                source_params=source.split(':')
                                dest_params=dest.split(':')
                                source_name=source_params[0]
                                source_port=source_params[1]
                                dest_name=dest_params[0]
                                dest_port=dest_params[1] 
                                if source_port==portid and dest_port==neighborportid and dest_n == dest1: 
                                    log.info("port "+portid+" of "+device_name+" Is Connected To Port "+neighborportid+" of "+dest1)
                                    count=count+1
                                    flag = 1
                                    break
                          if flag == 1:
                              flag=0
                              break
                if count==rise:
                    log.success('LLDP Neighbor Information Matched With The Given Information\n')
                    Result.append("Pass")
                else:
                    log.failure('LLDP Neighbor Information Does Not Matches With The Given Information\n')
                    Result.append("Fail") 
                count =0
                rise = 0
                list2=[]
        os.remove("sample.txt")
        if "Fail" in Result:
                    raise testfail.testFailed("LLDP neighbor information does not matches with the given information\n") 




def checkip(device,port=[],interface_ip=[]):
        count=0
        device_name=Device_parser(device)
        connectionInfo=Connect(device)
        connectionInfo.sendline("snap_cli")
        connectionInfo.expect(">")
        connectionInfo.sendline("enable")  
        connectionInfo.expect("#")
        connectionInfo.sendline("show run")  
        connectionInfo.expect("#")
        result= connectionInfo.before         
        log.details(result)
        fd = open("sample.txt","w+")
        fd.write(result)
        fd.close()
        f = open("sample.txt","r") 
        line = f.readlines()
        for i in range (0,len(port)):
            for eachline in range (len(line)):
                if port[i] in  line[eachline]:
                    if interface_ip[i] in line[eachline+1] :
                        count = count+1
        os.remove("sample.txt")
        if count == len(port):
            log.success("IP address is configured and verified on "+device_name)
        else :
            log.failure("IP address is not configured correctly on "+device_name)
           
           



def checkstate(device,port=[]):
        count=0
        device_name=Device_parser(device)
        connectionInfo=Connect(device)
        connectionInfo.sendline("snap_cli")
        connectionInfo.expect(">")
        connectionInfo.sendline("enable")  
        connectionInfo.expect("#")
        connectionInfo.sendline("show ip interface")  
        connectionInfo.expect("#")
        result= connectionInfo.before         
        log.details(result)
        fd = open("sample.txt","w+")
        fd.write(result)
        fd.close()
        f = open("sample.txt","r") 
        line = f.readlines()
        pattern = r'\s*(\w*)\s*(\d*\.\d*\.)\s*(\S*).*'
        for i in range (0,len(port)):
            for eachline in range (len(line)):
                match = re.search(pattern,line[eachline])
                if match:
                    if match.group(1) == port[i] and match.group(3) == "UP":
                         count= count+1
        os.remove("sample.txt")
        if count == len(port):
            log.success("port is UP on "+device_name)
        else :
            log.failure("port is not up on "+device_name)
           

   


def checkstate1(mode,fab_devices,csw_devices,asw_devices,fab=[],csw=[],asw=[],interface_dict={}) :
    list1=[]
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
                        #print json.dumps(create_IPv4Intf)
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
        
    for i in range(len(list1)):
            port = []
            device = list1[i]
            device_name=Device_parser(device)
            connectionInfo=Connect(device)
            connectionInfo.sendline("snap_cli")
            connectionInfo.expect(">")
            connectionInfo.sendline("enable")  
            connectionInfo.expect("#")
            for j in range(len(list1)):
                if device != list1[j] :
                    device_interface=device+"_"+list1[j]+"_eth"    
                    if device_interface in interface_dict.keys():
                        eth = interface_dict[device_interface]
                        port.append(eth)
            checkstate(device,port)
          
                      


           

def showrun(device,dec,*string):
        count=0
        device_name=Device_parser(device)
        connectionInfo=Connect(device)
        connectionInfo.sendline("snap_cli")
        connectionInfo.expect(">")
        connectionInfo.sendline("enable")  
        connectionInfo.expect("#")
        connectionInfo.sendline("show run")  
        connectionInfo.expect("#")
        result= connectionInfo.before         
        log.details(result)
        fd = open("sample.txt","w+")
        fd.write(result)
        fd.close()
        f = open("sample.txt","r") 
        line = f.readlines()
        for i in range (len(string)):
            if string[i] in line:
                count= count+1
        os.remove("sample.txt")
        if count == len(string):
            log.success(desc+" is configured and verified successfully")
             
   
def host(mode,fab_devices,csw_devices,asw_devices,fab=[],csw=[],asw=[],hostname={}):  

    list1=[]
    if mode == "no" :
        for i in range(0,int(fab_devices)) :
            list1.append(fab[i])
        for i in range(0,int(csw_devices)) :
            list1.append(csw[i])
        for i in range(0,int(asw_devices)) :
            list1.append(asw[i])
                        #print json.dumps(create_IPv4Intf)
    if mode == "yes":
        for i in fab:
            list1.append(i)
        for i in csw:
            list1.append(i)
        for i in asw:
            list1.append(i)
        print list1
    for i in range(len(list1)):
            port = []
            device = list1[i]
            device_name=Device_parser(device)
            connectionInfo=Connect(device)
            connectionInfo.sendline(hostname[list1[i]])
            connectionInfo.expect("#")
            
            
            
            
            
            
            

 
