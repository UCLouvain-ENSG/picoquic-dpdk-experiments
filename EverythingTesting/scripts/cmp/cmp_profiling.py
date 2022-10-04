

quiche = {}
quiche['name'] = 'quiche'
quiche['total'] = 84.4
quiche['crypto'] = 17.3
quiche['IO'] =  5.52

quicly = {}
quicly['name'] = 'quicly'
quicly['total'] = 19.9 + 76
quicly['crypto'] = 34.9 + 5.56
quicly['IO'] = 29.2 + 4.94

msquic = {}
msquic['name'] = 'msquic'
msquic['total'] = 88.9
msquic['crypto'] = 24.5
msquic['IO'] = 12.8

picoquic = {}
picoquic['name'] = 'picoquic'
picoquic['total'] = 87.4
picoquic['crypto'] = 31.6
picoquic['IO'] = 16.4

picoquic_dpdk = {}
picoquic_dpdk['name'] = 'picoquic_dpdk'
picoquic_dpdk['total'] = 84.9
picoquic_dpdk['crypto'] = 37.5
picoquic_dpdk['IO'] = 4.85

profiles = [quiche,quicly,msquic,picoquic,picoquic_dpdk]


def print_profile(profile):
    print("========")
    print("name : {}".format(profile['name']))
    total = profile['total']
    crypto = (profile['crypto']/total)*100
    io = (profile['IO']/total)*100
    stack = ((total-crypto-io)/total)*100
    
    print("IO : {}".format(io))
    print("crypto : {}".format(crypto))
    print("stack : {}".format(stack))
    
    print("========")
    
for p in profiles:
    print_profile(p)