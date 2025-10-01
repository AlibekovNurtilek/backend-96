#!/bin/bash

LOG_FILE="./backend.log"

echo "Остановка backend на порте 6400..." >> "$LOG_FILE" 2>&1
PID=$(lsof -t -i:6400)

if [ -n "$PID" ]; then
  kill -9 $PID >> "$LOG_FILE" 2>&1
  echo "Backend процесс на порте 6400 остановлен." >> "$LOG_FILE"
else
  echo "Нет процесса на порте 6400." >> "$LOG_FILE"
fi
