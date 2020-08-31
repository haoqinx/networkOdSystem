# What is the networkOdSystem?
A Detection system for abnormal network traffic in different application categories. Use custom nfstream, nDPI, Redis, Elasticsearch, logstash, Kibana, pyod and other technologies.
## Dependencies
1. redis running on port which decleared in ./config/config.ini
2. elasticsearch running on port 9200
3. kibana running on port 5601
## How to use system:
1. enter the dictionary
2. run command: sudo python main.py (which must be root)
## Add your own apps
1. Add a new app filter in ./lib/nDPI/, please refer to nDPI official documents for details.
2. Replace the libndpi.so file in nfstream with a custom compiled file created in step 1.
3. Add your app name to APP_LIST in main.py ,which must be consistent with the application_name detected by nfstream.		
4. Add your MODEL_FLAG_{APP} flag in main.py
5. Add the MODEL_FLAG_{APP} flag to MODEL_LIST in main.py