all_data = {'multiple' : [{'name': 'snmpsim', 'pull_count': 18}, {'name': 'cars-api', 'pull_count': 4}],
            'single':[{'name': 'snmpsim', 'pull_count': 18}],
            'empty':[]}

substreams = {'single':[{'date':'05-Oct-2020','image_name':'snmpsim'}],
              'multiple':[{'date':'05-Oct-2020','image_name':'snmpsim'},{'date':'05-Oct-2020','image_name':'cars-api'}],
              'empty':[]}

stats = {'single':[{'date':'05-Oct-2020','image_name':'snmpsim', 'pulls':18}],
         'multiple':[{'date':'05-Oct-2020','image_name':'snmpsim','pulls':18},
                     {'date':'05-Oct-2020','image_name':'cars-api','pulls':4}],
         'empty':[],
         'invalid':120}
output = {'valid' : "docker stats collected successfully", 'invalid' : "Error while writing into dynamodb table"}
handler_message = {'success' : ['data collected in docker_substreams table','data collected in docker_stats table'],
                   'failure' : ['Exception while inserting data into docker_substreams table',
                                'Exception while inserting data into docker_stats table']}
message = {'success' : 'data collected in {} table','failure' : 'Exception while inserting data into {} table'}
data_length = 6
table = {'substreams' : 'docker_substreams', 'stats' : 'docker_stats', 'fake_table' : 'Dummy_table'}
response = {'results':200}
url = 'url'
date = '05-Oct-2020'