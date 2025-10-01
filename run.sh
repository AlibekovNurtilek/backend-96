#!/bin/bash

LOG_FILE="./backend.log"

echo "Запуск backend на порте 6400..." >> "$LOG_FILE" 2>&1
uvicorn app.main:app --reload --host 0.0.0.0 --port 6400 >> "$LOG_FILE" 2>&1 &
echo "Backend запущен. Логи в $LOG_FILE" >> "$LOG_FILE"
