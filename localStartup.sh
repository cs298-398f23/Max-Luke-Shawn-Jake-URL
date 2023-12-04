#!/bin/bash
# Task 1: Start redis-server in the background
echo "Task 1: Starting redis-server in the background..."
redis-server &
# Add a delay to allow Redis server to start (adjust as needed)
sleep 2
echo "------------------------------------------------------------"
# Task 2: Run test.py
echo "Task 2: Running test.py..."
python3 test.py
echo "------------------------------------------------------------"
# Task 3: Run app.py
echo "Task 3: Running app.py..."
python3 app.py
echo "------------------------------------------------------------"
# Optional: Stop the Redis server after running your scripts
# Uncomment the line below if you want to stop the Redis server when the script is done
# redis-cli shutdown
echo "Goodbye!"