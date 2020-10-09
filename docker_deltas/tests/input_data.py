output_substreams = {'single_data':[{'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'}],
                        'multiple_data':[{'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
                                    {'date': '03-Sep-2020', 'image_name': 'cars-api'}]}
substreams =  {'single_substream':['qxf2_pom_essentials'],
               'multiple_substream':['qxf2_pom_essentials','cars-api'],
               'invalid':120}
substreams_data = {'yesterday_substreams':['qxf2_pom_essentials'], 'today_substreams':['qxf2_pom_essentials','cars-api']}
handler_substreams = {'single_data':['qxf2_pom_essentials'],'multiple_data':['qxf2_pom_essentials','cars-api']}
new_substreams =  ['cars-api']
docker_stats = {'single_stats':[{'pulls': 2657, 'date': '02-Sep-2020', 'image_name': 'qxf2_pom_essentials'}],
                'multiple_stats':[{'pulls': 2661, 'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials'},
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
read_error = 'Exception while reading data from {} table.'
key = {'docker':'image_name','github':'repo_name'}
table = {'stats':'docker_stats','substreams':'docker_substreams','dummy':'dummy_table'}
date = {'yesterday':'02-Sep-2020','today':'03-Sep-2020'}
key = 'image_name'
message = {'writing_success':'data collected in {} table','writing_failure':'Exception while inserting data into {} table'}
data = {'valid':[{'date': '03-Sep-2020', 'image_name': 'qxf2_pom_essentials', 'delta_pulls': 4}],
        'date_not_present':[{'image_name': 'qxf2_pom_essentials', 'delta_pulls': 4}],
        'image_name_not_present':[{'date': '03-Sep-2020', 'delta_pulls': 4}]}
reading_message = {'success':[{'pulls': 2657, 'date': '02-Sep-2020', 'image_name': 'qxf2_pom_essentials'}],
                   'failure':'Exception while reading data from test table.'}