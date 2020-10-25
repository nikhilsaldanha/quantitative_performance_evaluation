import pandas as pd

params = ["batch_size", "exec_mem", "num_exec", "cores_per_exec"]
param_map = {
    "batch_size": {
        -1: 128,
        1: 256
    },
    "exec_mem": {
        -1: "2G",
        1: "8G"
    },
    "num_exec": {
        -1: 1,
        1: 2
    },
    "cores_per_exec": {
        -1: 1,
        1: 2
    },
    "num_nodes": {
        -1: 1,
        1: 2
    }
}

df = pd.read_csv("exp.csv")

exps = []
workloads = ["bi-rnn", "lenet"]
schedulers = ["FAIR", "FIFO"]
nodess = [1, 2]
sparkgen_conf = {
                "jobClassParameters": [
                    
                ]
            }
for workload in workloads:
    for scheduler in schedulers:
        for nodes in nodess:

            for i in range(df.shape[0]):
                sched = df.loc[i, "sched"]
                num_nodes = df.loc[i, "num_nodes"]
                scheduler_matches = (scheduler == "FIFO" and sched == -1) or (scheduler == "FAIR" and sched == 1)
                nodes_match = (nodes == 1 and num_nodes == -1) or (nodes == 2 and num_nodes == 1)
                if scheduler_matches and nodes_match:
                    for r in range(3):
                        exp_no = df.loc[i, "exp_no"]
                        batch_size = param_map["batch_size"][df.loc[i, "batch_size"]]
                        exec_mem = param_map["exec_mem"][df.loc[i, "exec_mem"]]
                        num_exec = param_map["num_exec"][df.loc[i, "num_exec"]]
                        cores_per_exec = param_map["cores_per_exec"][df.loc[i, "cores_per_exec"]]
                        total_executor_cores = num_exec*cores_per_exec
                        num_nodes =  param_map["num_nodes"][df.loc[i, "num_nodes"]]
                        exp = f"./spark-submit --master spark://10.128.0.3:7077 \
                        --total-executor-cores {total_executor_cores} \
                        --executor-cores {cores_per_exec} \
                        --executor-memory {exec_mem} \
                        --py-files /home/am72ghiassi/bd/spark/lib/bigdl-0.11.0-python-api.zip,/home/am72ghiassi/bd/codes/{workload}.py \
                        --properties-file /home/am72ghiassi/bd/spark/conf/spark-bigdl.conf \
                        --jars /home/am72ghiassi/bd/spark/lib/bigdl-SPARK_2.3-0.11.0-jar-with-dependencies.jar \
                        --conf spark.driver.extraClassPath=/home/am72ghiassi/bd/spark/lib/bigdl-SPARK_2.3-0.11.0-jar-with-dependencies.jar \
                        --conf spark.executer.extraClassPath=bigdl-SPARK_2.3-0.11.0-jar-with-dependencies.jar  /home/am72ghiassi/bd/codes/{workload}.py \
                        --action train \
                        --batchSize {batch_size} \
                        --endTriggerType epoch \
                        --endTriggerNum 1 \
                        --dataPath /tmp/mnist > {exp_no}_{nodes}node_{scheduler}_{workload}.{r}.log"

                        exps.append(exp)
            
            exps_string = "\n".join(exps)
            with open(f"exps_{nodes}nodes_{scheduler}_{workload}.sh", "w") as f:
                f.write(exps_string)
            exps = []