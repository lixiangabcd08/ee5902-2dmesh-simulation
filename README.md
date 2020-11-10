# 2D NoC Routing Strategies & Performance Evaluation for SNN
Project for EE5902

## Files included
1. simulator.py
2. single_pkt_test.py
3. random_pkt_test.py
4. constant_pkt_test.py
5. router.py
6. modxy_router.py
7. a_router.py
8. elra_router.py
9. ca_router.py
10. heatmap.py
11. network_map.py
12. packet.py
13. packet_generator.py
14. receiver.py
15. sub_simulator_func.py
16. README.md

## Instructions
use simulator.py to run

### single packet test
--test_mode 0

### for random packet test
--test_mode 1 --load_cycles 100 --target_rate <fill in 0-10>

### for constant packet test
--test_mode 2


## parameters
1. --m, type=int, default=4
    - number of rows
2. --n, type=int, default=4
    - number of columns
3. --algo_type, type=int, default=0
    - 0:basic XY,
    - 1:modified XY,
    - 2:Adaptive Routing,
    - 3:ELRA,
    - 4:CA router
    - 5:all routers
4. --cycle_limit, type=int, default=500
5. --load_cycles, type=int. default=20
    - cycles to inject packets in test mode 2
6. --target_rate, type=float, default=5
    - rate to send spikes in test mode 1, keep sending 0-10 no sending
7. --test_mode, type=int, default=1
    - 0->single pkt test,
    - 1->random pkt test,
    - 2->congestion awareness test
8. --runs, type=int, default=1
    - number of runs in random pkt test
9. --verbose, type=int, default=0
    - 0->only num of pkt received per router
    - 1-> L0 + average clk cycles
    - 2-> L1 + all packet information
    - 3-> L2 + heatmap
10. --print_output, type=bool, default=True 
    - Whether to print simulator output in terminal
11. --sim_data_path, type=string, default="./sim_data.txt"
    - path to save the simulation data
12. --sim_summary_path, type=string, default="./sim_summary.txt"
    - path to save the simulation data summary, for random pkt test