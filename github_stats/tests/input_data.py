all_data = {'single' : ['qxf2/42Floors'],
            'multiple':['qxf2/42Floors','qxf2/bitcoin-info'],
            'empty' : []}
substreams = {'single':[{'date': '29-Sep-2020', 'repo_name': 'qxf2/42Floors'}],
              'multiple':[{'date': '29-Sep-2020', 'repo_name': 'qxf2/42Floors'},
                          {'date': '29-Sep-2020', 'repo_name': 'qxf2/bitcoin-info'}],
              'empty':[]}
stats = {'single':[{'date': '29-Sep-2020', 'repo_name': 'qxf2/42Floors', 'stars': 0, 'forks': 1, 'clones': 1, 'visitors': 1}],
         'multiple':[{'date': '29-Sep-2020', 'repo_name': 'qxf2/42Floors', 'stars': 0, 'forks': 1, 'clones': 1, 'visitors': 1},
                     {'date': '29-Sep-2020', 'repo_name': 'qxf2/bitcoin-info', 'stars': 1, 'forks': 3, 'clones': 6, 'visitors': 1}],
         'empty':[],
         'invalid':120}
output = {'success' : "github stats collected successfully", 'failure' : "Error while writing into dynamodb table"}
handler_message = {'success' : ['data collected in github_substreams table',
                                'data collected in github_stats table'],
                   'failure' : ['Exception while inserting data into github_substreams table',
                                'Exception while inserting data into github_stats table']}
message = {'success' : 'data collected in {} table','failure' : 'Exception while inserting data into table.'}
data_length = 40
table = {'substreams' : 'github_substreams', 'stats' : 'github_stats', 'fake_table' : 'Dummy_table'}
response = {'results':200}
current_date = '29-Sep-2020'
