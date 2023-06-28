#!/bin/bash
#SBATCH --job-name=dagstuhloid
#SBATCH --output=dagstuhloid_%j.out
#SBATCH --error=dagstuhloid_%j.err
#SBATCH --time=72:00:00
#SBATCH --partition=scavenge
#SBATCH --nodes=1
#SBATCH --cpus-per-task=67
#SBATCH -a 0-72


tasks=(keras_tuning mltuning naivemltuning seq_keras_tuning naive_seq_keras_tuning oneshot_mltuning seq_mltuning nano_seq_mltuning nano_naive_seq_mltuning naive_seq_mltuning bonnans yabbob reduced_yahdlbbbob yaconstrainedbbob yapenbbob yamegapenhdbbob yaonepenbigbbob yamegapenbigbbob yamegapenboxbbob yamegapenbbob yamegapenboundedbbob yapensmallbbob yapenboundedbbob yapennoisybbob yapenparabbob yapenboxbbob yaonepenbbob yaonepensmallbbob yaonepenboundedbbob yaonepennoisybbob yaonepenparabbob yaonepenboxbbob yahdnoisybbob yabigbbob yatuningbbob yatinybbob yasmallbbob yahdbbob yaparabbob yanoisybbob yaboundedbbob yaboxbbob pbbob boundedpbbob spsa_benchmark aquacrop_fao fishing rocket mono_rocket mixsimulator control_problem neuro_control_problem olympus_surfaces olympus_emulators simple_tsp complex_tsp sequential_fastgames powersystems mldakmeans double_o_seven multiobjective_example multiobjective_example_hd multiobjective_example_many_hd multiobjective_example_many photonics photonics2 pbo_reduced_suite causal_similarity unit_commitment team_cycling topology_optimization sequential_topology_optimization)

# SLURM_ARRAY_TASK_ID=154 # comment in for testing

task=${tasks[SLURM_ARRAY_TASK_ID]}

echo task attribution $SLURM_ARRAY_TASK_ID $task
python -m nevergrad.benchmark $task --num_workers=67
