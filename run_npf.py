#!/usr/bin/python
import sys

def npf_runner(stacks):
    supported_stack = ['picoquic','picoquic-dpdk','msquic','quiche','quicly','picotls']
    cmd = "python3 npf/npf-compare.py {}--test quic_tester_compare.npf --cluster client=client server=server"
    used_stacks = ''

    for stack in stacks:
        if stack not in supported_stack:
            print("Stack {} is not supported".format(stack))
            print("The supported stacks are : {}".format(supported_stack))
            return -1
        else if stack == 'picoquic' or stack == 'picoquic-dpdk':
            #building picotls requiered by picoquic and picoquic-dpdk
            subprocess.Popen((cmd + '--no-tests'.format('picotls').split(), stdout=subprocess.PIPE)

        else: 
            used_stacks+='{}+{} '.format(stack,stack)
    print(cmd.format(used_stacks))
    #subprocess.Popen(cmd.format(used_stacks).split(), stdout=subprocess.PIPE)
npf_runner(sys.argv[1:])

