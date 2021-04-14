output_substreams = {'single_data':[{'date':'12-Aug-2020','repo_name':'qxf2/qxf2-page-object-model'}],
                     'multiple_data':[{'date':'12-Aug-2020','repo_name':'qxf2/qxf2-page-object-model'},
                                      {'date':'12-Aug-2020','repo_name':'qxf2/python-exercises'}]}
substreams =  {'single_substream':['qxf2/qxf2-page-object-model'], 'multiple_substream':['qxf2_pom_essentials','cars-api']}
substreams_data = {'yesterday_substreams':['qxf2/qxf2-page-object-model'],
                   'today_substreams':['qxf2/qxf2-page-object-model','qxf2/python-exercises']}
handler_substreams = {'single_data':['qxf2/qxf2-page-object-model'],'multiple_data':['qxf2/qxf2-page-object-model',
                      'qxf2/python-exercises']}
new_substreams =  ['qxf2/python-exercises']
github_stats = {'single_stats':[{'date':'12-Aug-2020','clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,
                                 'visitors':159,'stars':134}],
                'multiple_stats':[{'date':'13-Aug-2020','repo_name':'qxf2/qxf2-page-object-model','stars':134,'forks':111,
                                   'clones':53,'visitors':154},
                                  {'date':'13-Aug-2020','clones':0,'repo_name':'qxf2/python-exercises','forks':0,
                                   'visitors':0,'stars':0}]}
handler_stats = [[{'date':'12-Aug-2020','clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,'visitors':159,'stars':134}],
                 [{'date':'13-Aug-2020','repo_name':'qxf2/qxf2-page-object-model','stars':134,'forks':111,'clones':53,'visitors':154},
                  {'date':'13-Aug-2020','clones':0,'repo_name':'qxf2/python-exercises','forks':0,'visitors':0,'stars':0}]]
amend_stats = {'new_yesterday_stats':[{'date':'12-Aug-2020','clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,
                                       'visitors':159,'stars':134},
                                      {'date': '12-Aug-2020','clones':0,'repo_name':'qxf2/python-exercises','forks':0,
                                       'visitors':0,'stars':0}]}
deltas = {'nonzero_delta':[{'date':'13-Aug-2020','repo_name':'qxf2/qxf2-page-object-model','delta_stars':0,'delta_forks':0,
                            'delta_clones':53,'delta_visitors':154},
                           {'date':'13-Aug-2020','repo_name':'qxf2/python-exercises','delta_stars':0,'delta_forks':0,
                            'delta_clones':0,'delta_visitors':0}]}
output = {'success':"github deltas collected successfully", 'failure':"Error while writing into dynamodb table"}
read_error = 'Exception while reading data from {} table.'
table = {'stats':'docker_stats','substreams':'docker_substreams','dummy':'dummy_table'}
date = {'yesterday':'12-Aug-2020','today':'13-Aug-2020'}
key = 'repo_name'
message = {'writing_success':'data collected in {} table','writing_failure':'Exception while inserting data into {} table'}
data = {'valid':[{'date':'12-Aug-2020','clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,'visitors':159,'stars':134}],
        'date_not_present':[{'clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,'visitors':159,'stars':134}],
        'image_name_not_present':[{'date':'12-Aug-2020','clones':55,'forks':111,'visitors':159,'stars':134}]}
reading_message = {'success':[{'date':'12-Aug-2020','clones':55,'repo_name':'qxf2/qxf2-page-object-model','forks':111,
                                 'visitors':159,'stars':134}]}
reading_substream = ['qxf2/qxf2-page-object-model']
