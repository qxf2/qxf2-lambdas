"""
The config file will list config details for aws configuration
"""
# settings for qxf2-employee-messages
log_group = '/aws/lambda/qxf2-employee-messages'

#settings for qxf2-skype-sender
query_skype_sender = f"fields @timestamp, @message ,Records.0.body|filter Records.0.attributes.SenderId = 'AROAUFFUKR766EKQRFECO:qxf2-employee-messages'"
log_group_bot_sender='/aws/lambda/qxf2-bot-sender'

# cloudwatch log dictionary keys
ptr_value = 'results_0_3_value'
record_body = 'logRecord_Records.0.body'
record_messageid = 'logRecord_Records.0.messageId'