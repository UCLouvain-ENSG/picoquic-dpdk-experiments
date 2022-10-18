#!/usr/bin/python
import sys
import argparse
from subprocess import Popen, PIPE

def npf_runner(stacks,client,server):
    supported_stack = ['picoquic','picoquic-dpdk','msquic','quiche','quicly','picotls']
    cmd = "python3 npf/npf-compare.py {}--test quic_tester_compare.npf --cluster client={} server={} --force-build"
    used_stacks = ''

    for stack in stacks:
        if stack not in supported_stack:
            print("Stack {} is not supported".format(stack))
            print("The supported stacks are : {}".format(supported_stack))
            return -1
        elif stack == 'picoquic' or stack == 'picoquic-dpdk':
            print("hello")
            #building picotls requiered by picoquic and picoquic-dpdk
            #subprocess.Popen((cmd + '--no-tests'.format('picotls').split(), stdout=subprocess.PIPE)
        else: 
            used_stacks+='{}+{} '.format(stack,stack)
    with Popen(cmd.format(used_stacks,client,server).split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='') # process line here
    
        

# Required positional argument

parser = argparse.ArgumentParser()

# Stacks used can be specified with --stacks
parser.add_argument('--stacks','--list', nargs='+', help='<Required> Set flag', required=True)
parser.add_argument('--client',type=str,required=True)
parser.add_argument('--server',type=str,required=True)

args = parser.parse_args()

npf_runner(args.stacks,args.client,args.server)

