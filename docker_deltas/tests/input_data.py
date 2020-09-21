response_substreams = [{'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
                       {'date': '03-Sep-2020', 'image_name': 'cars-api'}]
substreams =  {'yeaterday_substreams':['qxf2_pom_essentials'], 'today_substreams':['qxf2_pom_essentials','cars-api']}
handler_substreams = [['qxf2_pom_essentials'],['qxf2_pom_essentials','cars-api']]
new_substreams =  ['cars-api']
docker_stats = {'yesterday_stats':[{'pulls': 2657, 'date': '02-Sep-2020', 'image_name': 'qxf2_pom_essentials'}],
                'today_stats':[{'pulls': 2661, 'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
                               {'pulls': 0, 'date': '03-Sep-2020', 'image_name': 'cars-api'}]}
handler_stats = [[{'pulls': 2657, 'date': '02-Sep-2020', 'image_name': 'qxf2_pom_essentials'}],
                 [{'pulls': 2661, 'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
                  {'pulls': 0, 'date': '03-Sep-2020', 'image_name': 'cars-api'}]]
amend_stats = {'new_yesterday_stats':[{'pulls': 2657, 'date': '02-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
                                      {'pulls': 0, 'date': '02-Sep-2020', 'image_name': 'cars-api'}]}
deltas = {'nonzero_delta':[{'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials', 'delta_pulls': 4},
                           {'date': '03-Sep-2020', 'image_name': 'cars-api', 'delta_pulls': 0}],
          'zero_delta':[{'date': '20-Sep-2020', 'image_name': 'cars-api', 'delta_pulls': 0},
                        {'date': '20-Sep-2020', 'image_name': 'qxf2_pom_essentials', 'delta_pulls': 0}]}
output = {'success':"docker deltas collected successfully", 'failure':"Error while writing into dynamodb table"}
message = {'writing_success':'data collected in {} table','writing_failure':'Exception while inserting data into {} table'}
read_error = 'Exception while reading data from {} table.'
key = {'docker':'image_name','github':'repo_name'}
table = {'stats':'docker_stats','substreams':'docker_substreams','dummy':'dummy_table'}
date = '02-Sep-2020'