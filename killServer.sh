process_id=`ps aux | grep python | grep Yet | awk '{print $2}'`
kill $process_id
