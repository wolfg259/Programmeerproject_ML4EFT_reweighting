#!/bin/bash

PY='/data/theorie/pherbsch/miniconda3/envs/madgraph/bin/python'

function submit_job () {

  RUN_CARD=$1
  REP=$2
  COEFF=$3

  # create bash file to submit
  COMMAND=$PWD'/launch_rep_'$COEFF'_'$REP'.sh'

  # write launch command
  LAUNCH='export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/theorie/pherbsch/miniconda3/lib;'$PY' '$PWD'/training_init.py '$RUN_CARD' '$REP' '$COEFF

  echo $LAUNCH >> $COMMAND
  chmod +x $COMMAND
  chmod +x $PWD'/training_init.py'

  # submission
  qsub -q short -l walltime=00:10:00 -l nodes=1:ppn=1 -l pvmem=4000mb $COMMAND

#   qsub -q smefit -W group_list=smefit -l nodes=1:ppn=1 -l pvmem=4000mb $COMMAND
  rm $COMMAND

}

# SETUP

MCREPS=1

# tt -> llvlvlbb

RUN_CARD="/data/theorie/pherbsch/ML4EFT/subproj/code/runcards/ml_training/tt_shower/runcard_meeting_jaco.json"

coeff=( "ctu8")
# coeff=( "ctu8" "ctj8" "ctGRe_ctGRe" "ctGRe_ctj8" "ctj8_ctj8")

for c in "${coeff[@]}"
do
  for ((rep=0; rep < $MCREPS; rep++)); do
    submit_job $RUN_CARD $rep $c
  done
done