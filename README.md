# README
This repository is an ongoing work to monitor the performance of QUIC implementations. Currently the repository compares the following QUIC implementations : quicly, quiche, msquic, picoquic, picoquic-dpdk. To get a reference the repository also contains picotls. This project is an ongoing work to monitor the evolution of QUIC stacks, in the futur other stacks will be added.


# USAGE

This project relies on [NPF](https://github.com/tbarbette/npf) to build the different repositories, launch the measurements and graph the results. The npf_runner.sh launches npf
