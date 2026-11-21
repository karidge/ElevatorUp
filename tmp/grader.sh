#!/usr/bin/env bash

ASSIGNNAME="elevatorup"
EXPERS="1,1,25 2,2,25 50,16,10"
METRICS="stops maxq avgdelay stddelay"
GOLD_SEED=374837
GOLD_RUNS=500
EXAMPLE_SEEDS="646328 9 2800574"
EXAMPLE_N=3
EXAMPLE_RUNS=100
GRADE_SEED=229206
GRADE_RUNS=200

rubric_line_item()
{
	local i=`case $1:$2 in
		*:stops ) echo 0 ;; 
		*:maxq ) echo 1 ;; 
		*:avgdelay ) echo 2 ;; 
		*:stddelay ) echo 3 ;; 
	esac`
	expr 5 + $i
}


unpack_experiment()
{
	local floors=${1%,*}   #F,V
	local vators=${floors#*,}  #V
	local days=${1##*,}    #D
	floors=${floors%,*}        #F

	echo "floors=${floors}; vators=${vators}; days=${days};"
}

experiment()
{
	local theSIM="${1}"
	local exper="${2}"
	local RUNS="${3}"
	local SEED="${4}"		
	local touchformattingfile="${5:-/dev/null}"
	local missingdata=0
	local residfmt="__residual-%s-%s-%d.%s"
	local residrand
	local residoutput

	local floors
	local vators
	local days
	eval "`unpack_experiment ${2}`"

    for ((i=0; i<${RUNS}; i++)); do 
        test $(( $i % 50 )) -eq 0 && echo -n >&2 $i " "
        residrand=`printf ${5:-${residfmt}} $exper random $i dat 2>/dev/null`
        residoutput=`printf ${5:-${residfmt}} $exper output $i log 2>/dev/null`
        test_run -Q "${theSIM}" ${floors} ${vators} <(Random $(( SEED + i + j )) |tee "${residrand}" ) ${days} \
                | tee "${residoutput}" \
                | "${SIMGRADING}/output-pipe" | tr '\n' ' '  
        echo
	done | ( run_checknumeric f5+ f5+ f5+ f5+ && touch "${touchformattingfile}" ) | awk \
            -v dat1=__stops-${exper}-$SEED-$RUNS.dat \
            -v dat2=__maxq-${exper}-$SEED-$RUNS.dat \
            -v dat3=__avgdelay-${exper}-$SEED-$RUNS.dat \
            -v dat4=__stddelay-${exper}-$SEED-$RUNS.dat \
            '{ print $1 >dat1; print $2 >dat2; print $3 >dat3; print $4>dat4 }'
	echo ${RUNS} >&2

	for m in ${METRICS} ; do 
	    test `ncdat "__${m}-${exper}-${SEED}-${RUNS}.dat"` -ne ${RUNS} && missingdata=1   
	done

	for m in ${METRICS} ; do 
		for x in _${m}-${exper}-${SEED}-${RUNS}.dat ; do
			lineswithdata "_${x}" | sort -g |${SIMGRADING}/ecdf >${x}
		done
	done


	return ${missingdata}
}


###
# SIMS and usage should be defined before sourcing sim-lib.sh
###
SIMS=elevatorup
usage()
{
	cat <<EoT
ASSIGNMENT SPECIFIC OPTIONS 

  $ /assignment/specific/path/grader.sh . [RUNS [SEED]]

Where

  . is the SIM location (required first parameter)

  RUNS is the number of RUNS to use for SIM execution and plot generation

  SEED is a positive integer for a SEED to use for random file inputs

To retain residual data files to (maybe) assist in debugging, export

  $ export GRADER_SAVE_RESIDUALS=${SIMS}

EoT
}

# if SIMGRADING is unknown
test -z "${SIMGRADING}" -a -r ~khellman/SIMGRADING/sim-lib.sh && ~khellman/SIMGRADING/setup.sh ~khellman/SIMGRADING
if ! test -r "${SIMGRADING}/sim-lib.sh" ; then
	cat >&2 <<EoT
ERROR:  SIMGRADING is not in your environment or SIMGRADING/sim-lib.sh cannot
be found.  Have you followed the grader tarball setup.sh instructions on the
assignment's Wiki page?
EoT
	exit 1
fi

test -n "${SIMGRADING}" && source "${SIMGRADING}/sim-lib.sh"
source "${GRADERDIR}/grader-exec.sh"

set -e

RUNS=${1:-${GRADE_RUNS}}
SEED=${2:-${GRADE_SEED}}

tallydir=`create_tally_dir 1 TYPE=auto MAX=5 "Missing and truncated random.dat handled correctly"`
cat <<EoT |grader_msg 
Running SIM with non-existent trace file.  These runs should exit with non-zero
status and without OUTPUT lines...
EoT
set +e   # disregard exit status
for S in ${SIMS} ; do 
	tally_nonexist_tracefile "${tallydir}/dne-random" "${simloc}/SIM" 1 1 MISSINGRANDOM 1
	tally_truncated_tracefile "${tallydir}/trunc-random" "${simloc}/SIM" 10 10 TRUNCRANDOM_10 10
done




tally_consist_dir=`create_tally_dir    2 TYPE=auto MAX=5 'SCALE=floor MAX' "All values for consistency check are correct."`
test_sim_result()
{
	local exp=${1}
	local got=${2}
	local name=${3}
	local hexp=${4}
	local tallydir="${5}"
	tally_mark_bad "${tallydir}/${name}"
	if ! awk -v "e=${exp}" -v "g=${got}" 'BEGIN { if( sqrt((e-g)*(e-g)) > 1e-6 ) exit 1 ; else exit 0; }' ; then
		grader_msg << EoT
invocation
  ${simloc}/SIM ${FLOORS} ${VATORS} TRACEFILE ${DAYS}
should produce output value for '${name}' of ${hexp}, SIM produced '${got}' instead.
EoT
	else
		tally_mark_good "${tallydir}/${name}"
	fi
	return 0
}


tally_formatting_dir=`create_tally_dir 3 TYPE=auto MAX=4 'SCALE=floor MAX' "OUTPUT meets formatting requirements"`
tally_allresults_dir=`create_tally_dir 4 TYPE=auto MAX=5 'SCALE=floor MAX' 'SIM generates all results (no missing data points)'`
FLOORS=5
VATORS=500
DAYS=1
grader_msg <<EoT
Testing with FLOORS=${FLOORS} ELEVATORS=${VATORS} DAYS=${DAYS} as a consistency
check. Each person gets their own elevator (which is NOT the same as each
elevator is used exactly once...). Should result in output of 
  stops=2 maxq=0 avgdelay=0 stddelay=0 
EoT
test_run "${simloc}/SIM" ${FLOORS} ${VATORS} <("${SIMGRADING}/Random" ${SEED}) ${DAYS} | \
	"${SIMGRADING}/output-pipe" | ( tr '\n' ' '; echo ) | \
while read stops maxq avgdelay stddelay ; do
	test_sim_result       2.00000  ${stops}     STOPS        2.00000 "${tally_consist_dir}"
	test_sim_result       0        ${maxq}      MAXQ         0       "${tally_consist_dir}"
	avgdelay=${avgdelay/-0.00000/0.00000}
	avgdelay=${avgdelay/+0.00000/0.00000}
	test_sim_result       0.00000  ${avgdelay}  AVGDELAY     0.00000 "${tally_consist_dir}"
	test_sim_result       0.00000  ${stddelay}  STDDELAY     0.00000 "${tally_consist_dir}"
done
bad_consist_metrics=`find "${tally_consist_dir}" -name '*.bad' | while read b; do b="${b##*/}"; b="${b%.bad}"; echo ${b} ; done`
if test -z "${bad_consist_metrics}" >/dev/null ; then
	grader_msg <<EoT
Consistency check FLOORS=${FLOORS} ELEVATORS=${VATORS} DAYS=${DAYS} passed.
EoT
else
	grader_msg <<EoT
Consistency checks for ${bad_consist_metrics} failed.  CTRL-C now to inspect temporary files.
EoT
	grader_keystroke
fi
echo

if on_gradescope_image ; then 
	create_tally_dir  5 TYPE=man MAX=10 "STOPS results for three experiments" >/dev/null
	create_tally_dir  6 TYPE=man MAX=10 "MAXQ results for three experiments" >/dev/null
	create_tally_dir  7 TYPE=man MAX=10 "AVGDELAY results for three experiments" >/dev/null
	create_tally_dir  8 TYPE=man MAX=10 "STDDELAY results for three experiments" >/dev/null
	create_tally_dir  9 TYPE=man MAX=4  "Truncated Geometric(p) meets requirements" >/dev/null
	create_tally_dir 10 TYPE=man MAX=4  "Event List data structure meets requirements" >/dev/null
	create_tally_dir 11 TYPE=man MAX=4  "Uses Welford equations for AVGDELAY, STDDELAY and MAXQ" >/dev/null
	create_tally_dir 12 TYPE=man MAX=4  "Event(s) for elevator stops" >/dev/null
	create_tally_dir 13 TYPE=man MAX=5  "doc/README meets content requirements" >/dev/null
fi

grader_msg <<EoT
Running several SIM experiments with varying FLOORS, ELEVATORS, and DAYS.  This
may take some time ...
If the test exits with a "checknumeric" error, then one of your OUTPUT values
is improperly formatted (or missing data has confused the format analysis).
EoT
set -e
missingdata=0
for S in ${EXPERS} ; do
	eval "`unpack_experiment ${S}`"
	grader_msg <<EoT
Running FLOORS=${floors} ELEVATORS=${vators} DAYS=${days}
EoT
	tally_mark_good "${tally_allresults_dir}/${S}"
	experiment "${simloc}/SIM" ${S} ${RUNS} ${SEED} "${tally_formatting_dir}/${S}.good"

	if test $? -gt 0 ; then 
		# missing data
		tally_mark_bad "${tally_allresults_dir}/${S}"
		grader_msg <<EoT
ERROR: missing data for experiment ${S}.
EoT
		grader_keystroke
	fi

	if ! test -f "${tally_formatting_dir}/${S}.good" ; then 
		# formatting issue, error message has been displayed by checknumeric
		tally_mark_bad "${tally_formatting_dir}/${S}"
		grader_keystroke
	fi

    grader_msg <<EoT
... generating comparison plots for ${S} ...
EoT
    for x in ${METRICS} ; do 
		gplotpdf ${x} ${S} ${RUNS} ${SEED} `rubric_line_item $S $x`
    done

	grader_cleanup_experiment ${missingdata} "${METRICS}" "${S}" "${RUNS}" "${SEED}"

    grader_save_residuals ${S}

done

grader_signoff ${RUNS} ${SEED}

