import os,json
from Mi_Functions import *
from Params import *





dir_files=os.listdir('.')
html_files=[fil for fil in dir_files if fil.endswith('.html')]
nv_report_file=CHOOSE_OPTION_FROM_LIST_1(html_files,'Select your NV Report file: ')

csv_files=[fil for fil in dir_files if fil.endswith('.csv')]
email_csv_file=CHOOSE_OPTION_FROM_LIST_1(csv_files,'Select your exported "By Email" file: ')
rules_csv_file=CHOOSE_OPTION_FROM_LIST_1(csv_files,'Select your exported "Rules" file: ')

html_data=open(nv_report_file,'r').readlines()
nv_report_data=READ_CSV_AS_NESTED_LIST(nv_report_file)
nv_report_headers=nv_report_data[0]


for line in html_data:
    if 'var jsonReport =  ' in line:
        json_report=line[line.find('var jsonReport =  '):-2].replace('var jsonReport =  ','')
        #print json_report
        json_report=json.loads(json_report)
        #print json_report.keys()
    if 'var replayReportJson = ' in line:
        replay_report=line[line.find('var replayReportJson = '):-2].replace('var replayReportJson = ','')
        #print replay_report
        replay_report=json.loads(replay_report)
        #print replay_report.keys()


### Get relevant row from exported CSV file for data validation
exported_csv_data=READ_CSV_AS_NESTED_LIST(email_csv_file)
exported_csv_headers=exported_csv_data[0]
headers_as_dict={}
for h in exported_csv_headers:
    headers_as_dict.update({h:exported_csv_headers.index(h)})
SPEC_PRINT(headers_as_dict.keys())
tested_id=raw_input('Please enter your session ID (0682141b-43ef-4e40-a01d-58420e3c06da): ')
tested_id='0682141b-43ef-4e40-a01d-58420e3c06da'
for line in exported_csv_data:
    if line[headers_as_dict['id']]==tested_id:
        tested_line=line


### Check if duplicated in exported file ###
assert (len(exported_csv_data)==len(set([str(item) for item in exported_csv_data]))),'ERROR --> Duplicated lines in exported CSV file!!!'

# Check Email test #
assert (tested_line[headers_as_dict['email']]==replay_report['email']),'ERROR --> Email is not the same!!!'

# Check is_hpe
assert (str('@hpe.' in tested_line[headers_as_dict['email']].lower()).lower()==str(tested_line[headers_as_dict['is_hpe']]).lower()),'ERROR --> is_hpe is incorrect!!!'

# Check start time, DB based value #
sql="select created_at from sessions where id='"+tested_id+"';"
db_start_time=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,sql)[1][0]['created_at'].strftime("%Y-%m-%d %H:%M:%S")
exported_start_time=tested_line[headers_as_dict['start_time']]
assert (db_start_time==exported_start_time),'ERROR --> start time in DB is not the same as in Exported CSV file!!!'

# # Check device_type, DB based value
# sql="select properties from devices where id=(select device_id from sessions where id='"+tested_id+"');"
# db_device_type=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,sql)[1][0]['properties']
# exported_device_type=tested_line[headers_as_dict['device_type']]
# print db_device_type
# print exported_device_type
# assert (exported_device_type.lower() in db_device_type),'ERROR --> devuce type in DB is not the same as in Exported CSV file!!!'

# Check abandoned, DB based value
sql="select abandoned from sessions where id='"+tested_id+"';"
db_abandoned=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,sql)[1][0]['abandoned']
exported_abandoned=tested_line[headers_as_dict['abandoned']]
assert (str(db_abandoned).lower()==str(exported_abandoned).lower()),'ERROR --> abandoned in DB is not the same as in Exported CSV file!!!'

# Check error_code, DB based value
sql="select error_code from sessions where id='"+tested_id+"';"
db_error_code=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,sql)[1][0]['error_code']
exported_error_code=tested_line[headers_as_dict['error_code']]
assert (str(db_error_code).lower()==str(exported_error_code).lower()),'ERROR --> error_code time in DB is not the same as in Exported CSV file!!!'

# Check score (aggregateScoreMobile) in JSON (report_json)
json_score=json_report['transactionSummaries'][0]['summary']['aggregateScoreMobile']
exported_score=tested_line[headers_as_dict['score']]
assert (float(json_score)==float(exported_score)),'ERROR --> score is not the same!!!'

# Check duration, DB based value
session_start_sql="select created_at from sessions where id='"+tested_id+"';"
session_stop_sql="select completed_at from sessions where id='"+tested_id+"';"
start=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,session_start_sql)[1][0]['created_at']
stop=RUN_SQL(pg_db_name,pg_user,pg_ip,pg_pwd,pg_port,session_stop_sql)[1][0]['completed_at']
db_duration=int((stop-start).seconds)
exported_duration=tested_line[headers_as_dict['duration']]
assert (str(db_duration).lower()==str(exported_duration).lower()),'ERROR --> duration based DB calculation, is not the same as in Exported CSV file!!!'





