# README
This repository is an ongoing work to monitor the performance of QUIC implementations. Currently the repository compares the following QUIC implementations : quicly, quiche, msquic, picoquic, picoquic-dpdk. To get a reference the repository also contains picotls. This project is an ongoing work to monitor the evolution of QUIC stacks, in the futur other stacks will be added.


# USAGE

This project relies on [NPF](https://github.com/tbarbette/npf) to build the different repositories, launch the measurements and graph the results. The build process was not tested on many environments and may need modifications to fit your setup. The scripts [run_npf.py](run_npf.py) can be used to launch a comparison between selected stacks.

Example :

```
#launches a comparson between picoquic and msquic
python3 npf_runner.sh --stacks picoquic msquic --client client --server server
```

In the case of picoquic and picoquic-dpdk, a build of picotls is required, the script will build this repository first. Moreover picoquic_dpdk requieres a build of DPDK.

# CLUSTER

the cluster repository contains configs to connect to node through ssh. By passing --client=client and --server=server to run_npf.py those files will be used. It is also possible to specified a machine to use directly

Example :
``` 
--client=user01@server01.network.edu
```



