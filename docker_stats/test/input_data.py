all_data = {'valid_data' : [{'user': 'rohand','date':'21-Sep-2020','name':'cars_api', 'pull_count':3,'status':1}],
            'invalid_data' : [{'user': 'rohand','name':'cars_api', 'pull_count':3,'status':1}],'empty_data' : []}
prepared_data = {'nonempty_data' : [[{'date':'21-Sep-2020','image_name':'cars_api'}],[{'date':'21-Sep-2020','image_name':'cars_api', 'pulls':3}]],
                 'empty_data' : [[],[]]}
prepared = {'nonempty_substreams' : [{'date':'21-Sep-2020','image_name':'cars_api'}],
            'nonempty_stats' : [{'date':'21-Sep-2020','image_name':'cars_api', 'pulls':3}],
            'empty_data' : []}
output = {'valid' : "docker stats collected successfully", 'invalid' : "Error while writing into dynamodb table"}
handler_message = {'success' : ['data collected in docker_substreams table','data collected in docker_stats table'],
                   'failure' : ['Exception while inserting data into docker_substreams table','Exception while inserting data into docker_stats table']}
message = {'success' : 'data collected in {} table','failure' : 'Exception while inserting data into {} table'}
data_length = 6
table = {'substreams' : 'docker_substreams', 'stats' : 'docker_stats', 'fake_table' : 'Dummy_table'}
response = {'results':200}