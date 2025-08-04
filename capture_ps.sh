#
# Copyright 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# Define the path for the process snapshots
LOG_DIR="/opt/splunk/var/log/periodic_ps_snapshots"
mkdir -p "$LOG_DIR" # Ensure the directory exists

INTERVAL_SECONDS=2
DURATION_MINUTES=2 # Total duration for the loop
TOTAL_ITERATIONS=$(( (DURATION_MINUTES * 60) / INTERVAL_SECONDS ))

echo "--- Starting periodic process snapshot capture (every ${INTERVAL_SECONDS}s for ${DURATION_MINUTES}m) ---" | tee -a "$LOG_DIR/loop_events.log"

for (( i=1; i<=TOTAL_ITERATIONS; i++ )); do
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  OUTPUT_FILE="$LOG_DIR/ps_aux_$TIMESTAMP.log"

  # Capture ps aux output
  if command -v ps &> /dev/null; then
    ps aux > "$OUTPUT_FILE"
    # echo "Captured ps aux to $OUTPUT_FILE (Iteration $i/$TOTAL_ITERATIONS)" | tee -a "$LOG_DIR/loop_events.log"
  else
    echo "Error: 'ps' command not found in container. Cannot capture process list." | tee -a "$LOG_DIR/loop_events.log"
    break # Exit loop if ps is not found
  fi

  sleep $INTERVAL_SECONDS
done

echo "--- Finished periodic process snapshot capture ---" | tee -a "$LOG_DIR/loop_events.log"