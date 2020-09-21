all_data = {'nonempty_data' : ['qxf2/42Floors'],'empty_data' : []}
prepared_substreams = {'nonempty_data' : [{'date': '18-Sep-2020', 'repo_name': 'qxf2/42Floors'}],'empty_data' : []}
prepared_stats = {'nonempty_data' : [{'date': '18-Sep-2020', 'repo_name': 'qxf2/42Floors', 'stars': 0, 'forks': 1, 'clones': 2, 'visitors': 1}],'empty_data' : []}
output = {'success' : "github stats collected successfully", 'failure' : "Error while writing into dynamodb table"}
handler_message = {'success' : ['data collected in github_substreams table','data collected in github_stats table'],
                   'failure' : ['Exception while inserting data into github_substreams table','Exception while inserting data into github_stats table']}
message = {'success' : 'data collected in {} table','failure' : 'Exception while inserting data into {} table'}
data_length = 40
table = {'substreams' : 'github_substreams', 'stats' : 'github_stats', 'fake_table' : 'Dummy_table'}
response = {'results':200}
