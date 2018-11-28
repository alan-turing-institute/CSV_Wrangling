#!/bin/bash
#
# Bash wrapper around HypoParsr so we can kill the thing when it takes too 
# long.
#
# This is necessary because R's withTimeout can't kill C code so it's kinda 
# useless.
#
# Author: G.J.J. van den Burg
# Date: 2018-09-28T09:21:05+01:00
# Copyright (c) 2018 - The Alan Turing Institute
# License: See the LICENSE file.
#
#

TIMEOUT=600 # ten minutes

ALL_FILE="$1"
OUTPUT_FILE="$2"

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
HYPO_R="${THIS_DIR}/detection/hypo.R"

if [ ! -f ${HYPO_R} ]
then
	echo "Couldn't find hypo.R at ${HYPO_R}. Not starting."
	exit 1
fi

if [ ! -f ${OUTPUT_FILE} ]
then
	touch ${OUTPUT_FILE}
fi

# catch return code 124

for filename in `cat ${ALL_FILE}`
do
	# check if it is already processed
	if grep -q ${filename} ${OUTPUT_FILE}
	then
		echo "File ${filename} already processed."
		continue
	fi

	echo "[hypoparsr] Analyzing file: ${filename}"

	# process it with timeout
	res=$(timeout ${TIMEOUT} Rscript ${HYPO_R} ${filename} 2>/dev/null)

	# timeout retcode is 124 if timeout occurred.
	if [ "$?" -eq "124" ]
	then
		# timeout occurred
		res="{\"status\": \"FAIL\", \"status_msg\": \"TIMEOUT\", \"filename\": \"${filename}\", \"detector\": \"hypoparsr\", \"runtime\": ${TIMEOUT}, \"hostname\": \"$(hostname)\"}"
	fi

	# Strip the simpleError from the output if necessary
	res=$(echo "${res}" | grep -v simpleError | grep -v read_delim)

	echo "${res}" >> ${OUTPUT_FILE}
done
