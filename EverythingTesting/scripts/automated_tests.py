#!/usr/bin/env python3

from http import client
from pydoc import describe
from subprocess import Popen, PIPE
import subprocess

import json
import shlex
import time
import re
from toml import TomlDecodeError

def retrieve_cards(number):
    cards = open('/mnt/C072C89972C89616/school/memoire/MemoireRemote/dpdk_picoquic/EverythingTesting/scripts/cards.txt', 'r')
    nic_counter = 0
    ret = ''
    for card in cards:
        if re.search('Virtual Function',card):
            line_as_array = card.split()
            card_id = line_as_array[0]
            card_id = card_id[-7:]
            ret += '-a 0000:{} '.format(card_id)
            nic_counter+=1
            if nic_counter == number :
                return ret
    return ret


#Global variables
nsc='sudo ip netns exec nsCLIENT'
nss='sudo ip netns exec nsSERVER'

serverName = 'server'
clientName = 'client1'
process_name = 'dpdk_picoquicdemo'
dpdk1Client = '--dpdk -l 0-1 -a 0000:18:00.0 -- -A 50:6b:4b:f3:7c:70'
# dpdk15Client = '--dpdk -l 0-15 {} -- -A 50:6b:4b:f3:7c:70'.format(retrieve_cards(15))
dpdk8Client = '--dpdk -l 0-8 {} -- -A 50:6b:4b:f3:7c:70'.format(retrieve_cards(8))
dpdk1Server = '--dpdk -l 0-1 -a 0000:18:00.0 --'
dpdkVarServer = '--dpdk -l 0-{} -a 0000:18:00.0 --'
nodpdk = 'nodpdk'
dpdk_picoquic_directory = '/home/nikita/memoire/dpdk_picoquic'
wireguard_directory = '/home/nikita/memoire/wireguard'
picotls_directory = '/home/nikita/memoire/picotlsClean'
quiche_directory = '/home/nikita/memoire/quiche'
msquic_directory = '/home/nikita/memoire/msquic'
quicly_directory = '/home/nikita/memoire/quicly'
picotls_server_directory = '/home/nikita/memoire/picotlsClean'
picotls_client_directory = '/home/nikita/memoire/picotls_for_tests'



def dic_to_json(dic):
    return shlex.quote(json.dumps(dic))
    

def get_pid_process(host,name):
    cmds = ['ssh',host,'nohup','pidof',name]
    p = Popen(cmds, stdout=PIPE)
    return p.communicate()[0]

def kill_process(host,pid):
    cmds = ['ssh',host,'nohup','sudo kill',str(pid)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def run_command(command,host,directory):
    cmds = ['ssh', host,'cd {}; {}'.format(directory,command)]
    print(cmds)
    return Popen(cmds, stdout=None, stderr=None, stdin=None)
    
def run_command_read_STDOUT(command,host,directory):
    cmds = ['ssh', host,'cd {}; {}'.format(directory,command)]
    print(cmds)
    return Popen(cmds, stdout=subprocess.PIPE, stderr=None, stdin=None)

def run_client(args):
    cmds = ['ssh', clientName,'python3','/home/nikita/memoire/dpdk_picoquic/EverythingTesting/scripts/client_for_tests.py',dic_to_json(args)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def run_server(args):
    cmds = ['ssh', serverName,'python3','/home/nikita/memoire/dpdk_picoquic/EverythingTesting/scripts/server_for_tests.py',dic_to_json(args)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def test_generic(argsClient,argsServer,isComparison):
    # run_server(argsServer)
    # time.sleep(5)
    # client_process = run_client(argsClient)
    # client_process.wait()
    # pid = get_pid_process(serverName,process_name)
    # intPid = int(pid)
    # killing_process = kill_process(serverName,str(intPid))
    # killing_process.wait()
    
    if isComparison:
        argsClientNoDpdk = argsClient.copy()
        argsClientNoDpdk["eal"] = nodpdk
        argsClientNoDpdk["output_file"] = argsClientNoDpdk["output_file"].replace("dpdk","nodpdk")
        
        argsServerNoDpdk = argsServer.copy()
        argsServerNoDpdk["eal"] = nodpdk
        
        run_server(argsServerNoDpdk)
        client_process = run_client(argsClientNoDpdk)
        client_process.wait()
        pid = get_pid_process(serverName,process_name)
        intPid = int(pid)
        killing_process = kill_process(serverName,str(intPid))
        killing_process.wait()
    print("FINISHED")
    
    
def test_generic_repeting_client(argsClient,argsServer,isComparison,repetition):
    run_server(argsServer)
    time.sleep(5)
    for it in range(repetition):
        client_process = run_client(argsClient)
        client_process.wait()
        time.sleep(5)
    
    pid = get_pid_process(serverName,process_name)
    intPid = int(pid)
    killing_process = kill_process(serverName,str(intPid))
    killing_process.wait()
    
    if isComparison:
        argsClientNoDpdk = argsClient.copy()
        argsClientNoDpdk["eal"] = nodpdk
        argsClientNoDpdk["output_file"] = argsClientNoDpdk["output_file"].replace("dpdk","nodpdk")
        
        argsServerNoDpdk = argsServer.copy()
        argsServerNoDpdk["eal"] = nodpdk
        
        run_server(argsServerNoDpdk)
        for it in range(repetition):
            client_process = run_client(argsClientNoDpdk)
            client_process.wait()
            time.sleep(5)
        pid = get_pid_process(serverName,process_name)
        intPid = int(pid)
        killing_process = kill_process(serverName,str(intPid))
        killing_process.wait()    
    print("FINISHED")
    
def test_server_scaling():
    
    clientArgs = {"eal" : dpdk15Client,
                  "args": "-D ",
                  "output_file":"server_scaling_dpdk.txt",
                  "ip_and_port" : "10.100.0.2 5600",
                  "request" : "/10000000000",
                  "keyword" : "Mbps"}   
    serverArgs = {"eal" : dpdk1Server,
                  "args" : "",
                  "port" : "-p 5600"}
    for i in range(3,16):
        serverArgs["eal"] = 'dpdk -l 0-{} -a 0000:51:00.1 --'.format(i)
        clientArgs["output_file"] = "server_scaling_dpdk_{}.txt".format(str(i))
        test_generic(clientArgs,serverArgs,False)
        time.sleep(10)
    
 
## TP TESTS ##   
def test_throughput():
    ##Throughput test
    for it in range(15):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D",
                    "output_file":"throughputBBRFair_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,True)
        time.sleep(5)
        
def test_throughput256():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR256_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
def test_throughput128():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR128_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
def test_throughput20():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR20_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
## TP TESTS ##  
    
def test_throughput_without_encryption():
    ##Throughput test
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR_noEncryption_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/40000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
        
        
    
def test_handshake_simple():
    ##Throughput test
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"handshakeBBRfixed_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/8",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,50)
   
def test_RSS_15():
    for server_core in range(11,16): 
        clientArgsDpdk = {"eal" : dpdk15Client,
                    "args": "-D",
                    "output_file":"TP_{}core_dpdk.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
        
def test_RSS_8():
    for server_core in [5,6,7,8]: 
        clientArgsDpdk = {"eal" : dpdk8Client,
                    "args": "-D",
                    "output_file":"RSS/TP_{}core_dpdk_8_client.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "queueid"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
        
# def test_RSS_8_balance():
#     for server_core in [5,7,8]: 
#         clientArgsDpdk = {"eal" : dpdk8Client,
#                     "args": "-D",
#                     "output_file":"RSS/balance_{}core_dpdk_8_client.txt".format(str(server_core)),
#                     "ip_and_port" : "10.100.0.2 4443",
#                     "request" : "/200",
#                     "keyword" : "queueid"}
        
#         serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
#                     "args" : "",
#                     "port" : "-p 4443"}
#         test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,1)
#         time.sleep(5)
        
        
def test_RSS_8_balance():
    for nb_cores in [5,7,8]:
        cmdClient = ("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH /home/nikita/memoire/dpdk_picoquic/dpdk_picoquicdemo " 
        "--dpdk -l 0-8 -a 0000:18:00.2 -a 0000:18:00.3 -a 0000:18:00.4 -a 0000:18:00.5 -a 0000:18:00.6 -a 0000:18:00.7 -a 0000:18:01.0 -a 0000:18:01.1  "
        "-- -A 50:6b:4b:f3:7c:70 -D 10.100.0.2 4443 /200")
        
        cmdServer = ("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH "
        "/home/nikita/memoire/dpdk_picoquic/dpdk_picoquicdemo --dpdk -l 0-{} -a 0000:18:00.0 -- " 
        "-p 4443 | grep 'queueid' >> {}/EverythingTesting/data/RSS/balance_{}core_dpdk_8_client.txt").format(nb_cores,dpdk_picoquic_directory,str(nb_cores))
        
        server = run_command(cmdServer,serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command(cmdClient,clientName,dpdk_picoquic_directory)
        client.wait()
        killer = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        killer.wait()
        killer = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        killer.wait()
        time.sleep(3)
        
def test_RSS_8_balance_X():
    for nb_cores in [5,7,8]:
        cmdClient = ("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH /home/nikita/memoire/dpdk_picoquic/dpdk_picoquicdemo " 
        "--dpdk -l 0-8 -a 0000:18:00.2 -a 0000:18:00.3 -a 0000:18:00.4 -a 0000:18:00.5 -a 0000:18:00.6 -a 0000:18:00.7 -a 0000:18:01.0 -a 0000:18:01.1  "
        "-- -A 50:6b:4b:f3:7c:70 -D -X 10.100.0.2 4443 /200")
        
        cmdServer = ("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH "
        "/home/nikita/memoire/dpdk_picoquic/dpdk_picoquicdemo --dpdk -l 0-{} -a 0000:18:00.0 -- " 
        "-p 4443 | grep 'queueid' >> {}/EverythingTesting/data/RSS/balance_{}core_dpdk_8_client_X.txt").format(nb_cores,dpdk_picoquic_directory,str(nb_cores))
        
        server = run_command(cmdServer,serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command(cmdClient,clientName,dpdk_picoquic_directory)
        client.wait()
        killer = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        killer.wait()
        killer = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        killer.wait()
        time.sleep(3)
        
def test_RSS_8_X():
    for server_core in [8]: 
        clientArgsDpdk = {"eal" : dpdk8Client,
                    "args": "-D -X",
                    "output_file":"TP_{}core_dpdk_8_client_X.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
     
    
def test_handshake():
    #Testing handshake
    for it in range(10):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-H -D",
                    "output_file":"handshake_new_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/100",
                    "keyword" : "served"}   
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,True)
    
def test_request():
    #Testing requests
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"request_75_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "*75:/30000",
                "keyword" : "Mbps"}   
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
  
    
def test_batching():
    for it in range(5):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* 1 -@ 32 -G cubic",
                    "output_file":"throughput_1,32_fixed_80GBwrereceive_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/80000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : " -G cubic -* 1 -@ 32",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,False)
        time.sleep(5)
    time.sleep(10)
        
def test_batching_fixed_RX():
    for i in [4,8,16,32,64]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {} -@ 128 -G cubic".format(str(i)),
                        "output_file":"throughput_{}_fixed_10GB_RX128_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 4443",
                        "request" : "/20000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : " -G cubic -* {} -@ 128".format(str(i)),
                        "port" : "-p 4443"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
        
      
def test_batching_fixed_RX64():
    for i in [1,2,3,4,8,16,32,64]:
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* {} -@ 64".format(str(i)),
                    "output_file":"batching/throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(i)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "-* {} -@ 64".format(str(i)),
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,15)
        
def test_batching_fixed_TX64():
    for i in [4,8,16,32,64]:
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* 64 -@ {}".format(str(i)),
                    "output_file":"batching/throughput_{}_fixed_20GB_TX64_dpdk.txt".format(str(i)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "-* 64 -@ {}".format(str(i)),
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,15)
        
# def test_batching_fixed_RX64():
#     for i in [1,2,3,4,8,16,32,64]:
#         clientArgsDpdk = {"eal" : dpdk1Client,
#                     "args": "-D -* {} -@ 64".format(str(i)),
#                     "output_file":"throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(i)),
#                     "ip_and_port" : "10.100.0.2 4443",
#                     "request" : "/20000000000",
#                     "keyword" : "Mbps"}
        
#         serverArgsDpdk = {"eal" : dpdk1Server,
#                     "args" : "-* {} -@ 64".format(str(i)),
#                     "port" : "-p 4443"}
#         test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,15)
        
        
def test_batching2():
    for i in [1,2,4,8,16,32,64]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {}".format(str(i)),
                        "output_file":"throughput32_{}_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/80000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-* {}".format(str(i)),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)

def test_congestion_dpdk():
    for CC in ["reno", "cubic", "bbr", "fast"]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -G {} -* 1".format(CC),
                        "output_file":"CC_{}_dpdk.txt".format(CC),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/2000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-G {} -* 1".format(CC),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
def test_congestion_big_dpdk():
    for CC in ["reno", "cubic", "bbr", "fast"]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -G {} -* 32".format(CC),
                        "output_file":"CC_big_{}_dpdk.txt".format(CC),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/10000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-G {} -* 32".format(CC),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
def test_congestion_nodpdk():
    clientArgsDpdk = {"eal" : nodpdk,
                        "args": "-D",
                        "output_file":"CC_nodpdk.txt",
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/2000000",
                        "keyword" : "Mbps"}
            
    serverArgsDpdk = {"eal" : nodpdk,
                        "args" : " ",
                        "port" : "-p 5600"}
    test_generic(clientArgsDpdk,serverArgsDpdk,False)
    
def test_batching_noCC_noPacing():
    for i in [4,8,16,32,64,128]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {} -@ {}".format(str(i),str(i)),
                        "output_file":"throughput_noCC_noPacing_{}_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/20000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-* {} -@ {}".format(str(i),str(i)),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)


#############PROXY TESTING#####################

def clean_everything():
    p1 = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    p2 = run_command("sh killForwarder.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    p3 = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    p4 = run_command("sh killUDP.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    p5 = run_command("sudo kill $(pidof cli) >> /dev/null",clientName,dpdk_picoquic_directory)
    p6 = run_command("sudo kill $(pidof secnetperf) >> /dev/null",serverName,dpdk_picoquic_directory)
    p7 = run_command("sudo kill $(pidof generic-http3-server) >> /dev/null",serverName,dpdk_picoquic_directory)
    for p in [p1,p2,p3,p4,p5,p6,p7]:
        p.wait()
    
def proxy_TCP_testing():
    #dpdk proxy
    def mykiller():
        p1a = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p1b = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        p2a = run_command("sh killiperf3.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p2b = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        p3a = run_command("sh killForwarder.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p3b = run_command("sh killForwarder.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        for p in [p1a,p1b,p2a,p2b,p3a,p3b]:
            p.wait()
        
    server = run_command("sh network_scripts/proxy_setup_server_Z.sh",serverName,dpdk_picoquic_directory)
    server.wait()
    client = run_command("sh network_scripts/proxy_setup_client_Z.sh",clientName,dpdk_picoquic_directory)
    client.wait()
    # for i in range(5):
    #     for size in range(100,1300,100):
    #         serverP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP1 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/proxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
    #         clientP2.wait()
    #         mykiller();
    #         time.sleep(3);
            
    # for i in range(5):
    #     for size in range(100,1300,100):
    #         serverP1 = run_command("sh exec_scripts/serverNoDPDKProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP1 = run_command("sh exec_scripts/clientNoDPDKProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/proxyTCPNoDPDK{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
    #         clientP2.wait()
    #         mykiller();
    #         time.sleep(3);
       
    for i in range(5):
        for size in range(100,1300,100):        
            serverP1 = run_command("sh exec_scripts/dpdk_relay2.sh >> /dev/null",serverName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP1 = run_command("sh exec_scripts/dpdk_relay1.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/noproxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            clientP2.wait()
            mykiller();
            time.sleep(3);
            
           
def proxy_TCP_noDPDK():
    server = run_command("sh network_scripts/proxy_setup_server.sh",serverName,dpdk_picoquic_directory)
    server.wait()
    for i in range(5):
        for size in range(100,1300,100):
            clientP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP2 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " iperf3 -s >> /dev/null",serverName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP1 = run_command(nsc + " iperf3 -M {} -c 10.10.0.2 -t 30 >> EverythingTesting/data/proxy/proxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            serverP1.wait()
            clean_everything();
            time.sleep(3);




def proxy_UDP_testing_simple():
    #dpdk proxy
    # # server.wait()
    def mykiller():
        p1 = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p2 = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        p3 = run_command("sudo kill $(pidof udpsender)",serverName,dpdk_picoquic_directory)
        for p in [p1,p2,p3]:
            p.wait()
            
    cmd1 = run_command("sudo ip -all netns delete  ",serverName,dpdk_picoquic_directory)
    cmd1.wait()
    cmd1 = run_command("sudo ip -all netns delete  ",clientName,dpdk_picoquic_directory)
    cmd1.wait()
    for i in range(10):
        for size in range(100,1300,100):
            serverP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP1 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP2 = run_command("sh exec_scripts/proxy2.sh | grep 'final' >> EverythingTesting/data/proxy/proxyUDP{}.txt".format(size),clientName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP2 = run_command('sh exec_scripts/proxy1.sh {} 1 >> /dev/null'.format(size),serverName,dpdk_picoquic_directory)
            serverP2.wait()
            mykiller()
            time.sleep(3);
             
def proxy_UDP_testing():
    #dpdk proxy
    # # server.wait()
    cmd = run_command("sudo ip -all netns delete  ",serverName,dpdk_picoquic_directory)
    cmd.wait()
    
    cmd = run_command("sudo ip -all netns delete  ",clientName,dpdk_picoquic_directory)
    cmd.wait()

    cmd = run_command("sh network_scripts/proxy_setup_server_Z.sh",serverName,dpdk_picoquic_directory)
    cmd.wait()
    
    cmd2 = run_command("sh network_scripts/proxy_setup_client_Z.sh",clientName,dpdk_picoquic_directory)
    cmd2.wait()
    mydic = {}
    mydic['100'] = range(800,2000,200)
    mydic['200'] = range(1500,4200,200)
    mydic['300'] = range(1500,4000,300)
    mydic['400'] = range(2,7200,400)
    mydic['500'] = range(5000,7500,400)
    mydic['600'] = range(7000,9000,400)
    mydic['700'] = range(7200,9000,400)
    mydic['800'] = range(7500,9300,400)
    mydic['900'] = range(7500,9500,400)
    mydic['1000'] = range(8000,11500,400)
    mydic['1100'] = range(9000,12000,400)
    mydic['1200'] = range(9000,12500,400)
    
   
    
    for i in range(5):
        cmd1 = nss + " iperf3 -s -p 5000 -f m >> /dev/null"
        cmd2 = nss + " iperf3 -s -p 5001 -f m >> /dev/null"
        cmd = "{} & {}".format(cmd1,cmd2)
        Server = run_command(cmd,clientName,dpdk_picoquic_directory)
        time.sleep(5)
        for size in range(100,1300,100):
            my_range = [int(x/2) for x in mydic[str(size)]]
            for b in my_range:
                formater1 = run_command("echo -n {} Mbps iteration : {} \t >> EverythingTesting/data/proxy/proxyUDP{}_1.txt".format(b,i,size),clientName,dpdk_picoquic_directory)
                formater2 = run_command("echo -n {} Mbps iteration : {} \t >> EverythingTesting/data/proxy/proxyUDP{}_2.txt ".format(b,i,size),clientName,dpdk_picoquic_directory)
                formater1.wait()
                formater2.wait()
                serverP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
                time.sleep(5)
                clientP1 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
                time.sleep(5)
                cmd1 = nsc + " iperf3 -c 3.0.0.1 --cport 5500 -p 5000 -l {} -u -b {}M -t 10 -f m | grep 'receiver' >> EverythingTesting/data/proxy/proxyUDP{}_1.txt".format(size,b,size)
                cmd2 = nsc + " iperf3 -c 3.0.0.1 --cport 5600 -p 5001 -l {} -u -b {}M -t 10 -f m | grep 'receiver' >> EverythingTesting/data/proxy/proxyUDP{}_2.txt".format(size,b,size)
                cmd = "{} & {}".format(cmd1,cmd2)
                Cli = run_command(cmd,serverName,dpdk_picoquic_directory)
                Cli.wait()
                time.sleep(2)
                killer = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
                killer.wait()
                killer = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
                killer.wait()
        killer = run_command("sh killiperf3.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        killer.wait()         
            
def wireguard_testing():
    cmd1 = run_command("sudo ip -all netns delete  ",serverName,dpdk_picoquic_directory)
    cmd1.wait()
    cmd1 = run_command("sudo ip -all netns delete  ",clientName,dpdk_picoquic_directory)
    cmd1.wait()
    cmd2 = run_command("sh network_scripts/wireguard_server_setup.sh",serverName,dpdk_picoquic_directory)
    cmd2.wait()
    cmd3 = run_command("sh network_scripts/wireguard_client_setup.sh",clientName,dpdk_picoquic_directory)
    cmd3.wait()
    server = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
    time.sleep(5)
    for i in range(5):
        for size in range(100,1300,100):
            client = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/wireguardTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            client.wait()
            time.sleep(3)
    

#############PROXY TESTING#####################



#############Big Comparison Tests#####################

def picotls_test():
    # for setup in [""]:
    for setup in ["taskset -c 2","taskset -c 4",""]:
        for i in range(10):
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            server = run_command(("sudo {} ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
                                  "{}/EverythingTesting/data/cmp/picotls_ctesting{}.txt").format(setup,dpdk_picoquic_directory,clean_setup),serverName,picotls_directory)
            time.sleep(3)
            client = run_command("sudo {} ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256".format(setup),clientName,picotls_directory)
            time.sleep(30)
            killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
            killer1.wait()
            killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
            killer2.wait()
            time.sleep(5)
            

def picotls_LRO_TSO_test():
    
    # cmd = run_command("sudo ethtool -K ens1f0 lro off",serverName,dpdk_picoquic_directory)
    # cmd.wait()
    # cmd = run_command("sudo ethtool -K ens1f0 lro off",clientName,dpdk_picoquic_directory)
    # cmd.wait()
    # for i in range(10):
    #     server = run_command(("sudo ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
    #                               "{}/EverythingTesting/data/cmp/picotls_ctesting_no_LRO.txt").format(dpdk_picoquic_directory),serverName,picotls_directory)
    #     time.sleep(3)
    #     client = run_command("sudo ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256",clientName,picotls_directory)
    #     time.sleep(30)
    #     killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
    #     killer1.wait()
    #     killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
    #     killer2.wait()
    #     time.sleep(5)
        
    # cmd = run_command("sudo ethtool -K ens1f0 tso off",serverName,dpdk_picoquic_directory)
    # cmd.wait()
    # cmd = run_command("sudo ethtool -K ens1f0 tso off",clientName,dpdk_picoquic_directory)
    # cmd.wait()
    
    # for i in range(10):
    #     server = run_command(("sudo ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
    #                               "{}/EverythingTesting/data/cmp/picotls_ctesting_no_LRO_no_TSO.txt").format(dpdk_picoquic_directory),serverName,picotls_directory)
    #     time.sleep(3)
    #     client = run_command("sudo ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256",clientName,picotls_directory)
    #     time.sleep(30)
    #     killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
    #     killer1.wait()
    #     killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
    #     killer2.wait()
    #     time.sleep(5)
    
    # cmd = run_command("sudo ethtool -K ens1f0 gso off",serverName,dpdk_picoquic_directory)
    # cmd.wait()
    # cmd = run_command("sudo ethtool -K ens1f0 gso off",clientName,dpdk_picoquic_directory)
    # cmd.wait()
    
    # for i in range(10):
    #     server = run_command(("sudo ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
    #                               "{}/EverythingTesting/data/cmp/picotls_ctesting_no_LRO_no_TSO_no_GSO.txt").format(dpdk_picoquic_directory),serverName,picotls_directory)
    #     time.sleep(3)
    #     client = run_command("sudo ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256",clientName,picotls_directory)
    #     time.sleep(30)
    #     killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
    #     killer1.wait()
    #     killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
    #     killer2.wait()
    #     time.sleep(5)
        
    cmd = run_command("sudo ethtool -K ens1f0 gro off",serverName,dpdk_picoquic_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 gro off",clientName,dpdk_picoquic_directory)
    cmd.wait()
    
    
    for i in range(10):
        server = run_command(("sudo ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
                                  "{}/EverythingTesting/data/cmp/picotls_ctesting_no_GRO.txt").format(dpdk_picoquic_directory),serverName,picotls_directory)
        time.sleep(3)
        client = run_command("sudo ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256",clientName,picotls_directory)
        time.sleep(30)
        killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
        killer1.wait()
        killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
        killer2.wait()
        time.sleep(5)
    
    
def reset_nics():
    cmd = "sudo ethtool -K ens1f0 lro on && sudo ethtool -K ens1f0 tso on && sudo ethtool -K ens1f0 gro on && sudo ethtool -K ens1f0 gso on"
    run_cmd = run_command(cmd, clientName,quiche_directory)
    run_cmd.wait()
    run_cmd = run_command(cmd, serverName,quiche_directory)
    run_cmd.wait()

def picotls_full_testing_test():
    visited = []
    reset_nics()
    for param1 in ["lro","gro","gso","tso"]:
        for param2 in ["lro","gro","gso","tso"]:
            for param3 in ["lro","gro","gso","tso"]:
                for param4 in ["lro","gro","gso","tso"]:
                    params = [param1, param2, param3, param4]
                    params = list(set(params))
                    params.sort()
                    params_str = ' '.join(params)
                    if params_str not in visited:
                        visited.append(params_str)
                        description = ''
                        for p in params:
                            description += ("_no" + p)
                            cmd = run_command("sudo ethtool -K ens1f0 {} off".format(p), clientName,quiche_directory)
                            cmd.wait()
                            cmd = run_command("sudo ethtool -K ens1f0 {} off".format(p), serverName,quiche_directory)
                            cmd.wait()
                        for i in range(5):
                            server = run_command(("sudo ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
                                                    "{}/EverythingTesting/data/cmp/picotls/picotls_ctesting{}.txt").format(dpdk_picoquic_directory,description),serverName,picotls_directory)
                            time.sleep(3)
                            client = run_command("sudo ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256",clientName,picotls_directory)
                            time.sleep(30)
                            killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
                            killer1.wait()
                            killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
                            killer2.wait()
                            time.sleep(5)
                    reset_nics()
                    

  
def picotls_testing_no_gro_no_lro_no_sg_test():
    
    reset_nics()
    cmd = run_command("sudo ethtool -K ens1f0 lro off", clientName,quiche_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 lro off", serverName,quiche_directory)
    cmd.wait()
    
    cmd = run_command("sudo ethtool -K ens1f0 gro off", clientName,quiche_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 gro off", serverName,quiche_directory)
    cmd.wait()
    
    cmd = run_command("sudo ethtool -K ens1f0 tso off", clientName,quiche_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 tso off", serverName,quiche_directory)
    cmd.wait()
    
    cmd = run_command("sudo ethtool -K ens1f0 gso off", clientName,quiche_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 gso off", serverName,quiche_directory)
    cmd.wait()
    
    cmd = run_command("sudo ethtool -K ens1f0 sg off", clientName,quiche_directory)
    cmd.wait()
    cmd = run_command("sudo ethtool -K ens1f0 sg off", serverName,quiche_directory)
    cmd.wait()
                            
    for setup in ["taskset -c 2","taskset -c 4",""]:
        for i in range(10):
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            server = run_command(("sudo {} ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256 &>> "
                                  "{}/EverythingTesting/data/cmp/picotls_no_gro_no_lro_no_tso_no_gso_no_sg_ctesting{}.txt").format(setup,dpdk_picoquic_directory,clean_setup),serverName,picotls_directory)
            time.sleep(3)
            client = run_command("sudo {} ./cli 10.100.0.2 -B 8443 -y aes128gcmsha256".format(setup),clientName,picotls_directory)
            time.sleep(30)
            killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
            killer1.wait()
            killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
            killer2.wait()
            time.sleep(5)
                          

def quiche_test():
    for setup in ["taskset -c 2","taskset -c 4",""]:
    # for setup in [""]:
    # for setup in ["-c 0,16"]:
        for i in range(5):
            server = run_command("sudo {} ./target/release/examples/http3-server -p 4445 -k cert.key -c cert.crt".format(setup),serverName,quiche_directory)
            time.sleep(5)
            
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            
            client = run_command("sudo {} ./target/release/examples/http3-client -G 10000000000 -X keys.log 10.100.0.2 4445 >> {}/EverythingTesting/data/cmp/quiche_ctesting{}.txt"
                                 .format(setup,dpdk_picoquic_directory,clean_setup),clientName,quiche_directory)
            client.wait()
            killer = run_command("sudo kill $(pidof http3-server) >> /dev/null",serverName,dpdk_picoquic_directory)
            killer.wait()
            time.sleep(5)
    
def picoquic_test():
    for setup in ["taskset -c 2","taskset -c 4",""]:
    #for setup in ["-c 2","-c 4","-c 4,6"]:
        for i in range(15):
            server = run_command("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH {} ./dpdk_picoquicdemo --nodpdk -p 4443 -1"
                                 .format(setup),serverName,dpdk_picoquic_directory)
            time.sleep(5)
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            client = run_command(("sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH {} ./dpdk_picoquicdemo --nodpdk -D 10.100.0.2 4443 /20000000000 >> " 
                                  "{}/EverythingTesting/data/cmp/picoquic_ctesting{}.txt").format(setup, dpdk_picoquic_directory,clean_setup),
                                 clientName,dpdk_picoquic_directory)
            client.wait()
            time.sleep(5)
    
def msquic_test():
    for setup in [""]:
    # for setup in [""]:
        for i in range(15):
            server = run_command("sudo {} ./artifacts/bin/linux/x64_Release_openssl/secnetperf -cipher:1 -bind:10.100.0.2"
                                 .format(setup),serverName,msquic_directory)
            time.sleep(5)
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            client = run_command("sudo {} ./artifacts/bin/linux/x64_Release_openssl/secnetperf -cipher:1 -TestName:throughput -target:10.100.0.2 -p 4443 -download:20000000000 >> {}/EverythingTesting/data/cmp/msquic_ctesting_no_GRO{}.txt".
                                 format(setup, dpdk_picoquic_directory,clean_setup),clientName,msquic_directory)
            client.wait()
            killer = run_command("sudo kill $(pidof secnetperf) >> /dev/null",serverName,dpdk_picoquic_directory)
            killer.wait()
            time.sleep(3)
            
            
def quicly_test():
    for setup in ["taskset -c 2","taskset -c 4",""]:
    #for setup in ["-c 2","-c 4","-c 4,6"]:
        for i in range(15):
            server = run_command("sudo {} ./cli -c server.cert -k server.key 10.100.0.2 4433 -b 10000000000 -G"
                                 .format(setup),serverName,quicly_directory)
            time.sleep(5)
            clean_setup = setup.replace("taskset ","")
            clean_setup = clean_setup.replace(" ", "-")
            client = run_command(("sudo {} ./cli -p /20000000000 10.100.0.2 4433 -O -b 10000000000 -G >> " 
                                  "{}/EverythingTesting/data/cmp/quicly_ctesting{}.txt").format(setup, dpdk_picoquic_directory,clean_setup),
                                 clientName,quicly_directory)
            client.wait()
    
    
    
def request_test_picotls():
    test_time = 10
    trickery = """| grep "nb_handshakes : [0-9]"  | awk '{ SUM += $3} END { print SUM }'"""
    server = run_command("sudo taskset -c 4 ./cli -c server.cert -k server.key 10.100.0.2 8443 -B -y aes128gcmsha256",serverName,picotls_server_directory)
    time.sleep(5)
    for i in range(5):
        for nb_clients in [4,8,16,32,64,128]:
            client = run_command("""sudo ./cli --client {} {} 10.100.0.2 -B 8443 -y aes128gcmsha256 {} >> {}/EverythingTesting/data/cmp/handshakes/picotls_{}_clients_with_irqbalance.txt"""
                                .format(str(test_time),str(nb_clients),trickery,dpdk_picoquic_directory,str(nb_clients)),clientName,picotls_client_directory)
            client.wait()
            time.sleep(15);
    
    
    
    
    
    

#############Big Comparison Tests#####################







########################INTEROP#######################





def interop_test():
    for i in range(5):
        server = run_command("sh exec_scripts/newServer.sh",serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command("sh exec_scripts/client.sh >> {}/EverythingTesting/data/cmp/clientNoDPDKInterop.txt".format(dpdk_picoquic_directory),clientName,dpdk_picoquic_directory)
        client.wait()
        time.sleep(3)
        
    for i in range(5):
        server = run_command("sh exec_scripts/server.sh",serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command("sh exec_scripts/newClient.sh >> {}/EverythingTesting/data/cmp/clientDPDKInterop.txt".format(dpdk_picoquic_directory),clientName,dpdk_picoquic_directory)
        client.wait()
        time.sleep(3)
        
def interop_test_2():
    for i in range(5):
        server = run_command("sh exec_scripts/newServer.sh",serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command("sh exec_scripts/client.sh >> {}/EverythingTesting/data/cmp/clientNoDPDKInteropNoPatch.txt".format(dpdk_picoquic_directory),clientName,dpdk_picoquic_directory)
        client.wait()
        time.sleep(3)
        
    for i in range(5):
        server = run_command("sh exec_scripts/server.sh",serverName,dpdk_picoquic_directory)
        time.sleep(3)
        client = run_command("sh exec_scripts/newClient.sh >> {}/EverythingTesting/data/cmp/clientDPDKInteropNoPatch.txt".format(dpdk_picoquic_directory),clientName,dpdk_picoquic_directory)
        client.wait()
        time.sleep(3)
        
########################INTEROP#######################

if __name__ == "__main__":
    #test_handshake()
    #test_server_scaling()
    #test_batching2()
    #test_congestion_dpdk()
    #test_congestion_nodpdk()
    #test_batching_noCC_noPacing()
    #test_congestion_big_dpdk()
    #test_batching()
    #test_batching()
    #test_throughput()
    #test_handshake_simple()
    #test_handshake()
    #test_request()
    #test_RSS_15()
    #test_throughput_without_encryption()
    #test_RSS_8()
    #test_RSS_8_X()
    #test_throughput256()
    #test_throughput128()
    #test_throughput20()
    #test_batching_fixed_RX64()
    #proxy_UDP_testing()
    #proxy_UDP_testing()
        
    #picoquic_test()
    #picotls_test()
    #quiche_test()
    #msquic_test()
    #test_request()
    # test_batching_fixed_RX64()
    # time.sleep(15)
    # test_batching_fixed_TX64()
    #wireguard_testing()
    #proxy_UDP_testing()
    #proxy_TCP_testing()
    #test_throughput()
    #proxy_UDP_testing()
    #proxy_UDP_testing_simple()
    
    #test_RSS_8()
    
    #print(retrieve_cards(8))
    
    # test_RSS_8_balance()
    # test_RSS_8_balance_X()
    
    # interop_test_2()
    
    #quiche_test()
    #msquic_test()
    # picoquic_test()
    #picotls_test()
    #picoquic_test()
    #picotls_test()
    #picotls_LRO_TSO_test()
    #msquic_test()
    #picotls_full_testing_test()
    #picotls_testing_no_gro_no_lro_test()
    #quicly_test()
    # picotls_testing_no_gro_no_lro_no_sg_test()
    request_test_picotls()
