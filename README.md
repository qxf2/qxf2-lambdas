## A collection of lambdas used at Qxf2

AWS lambda function used by Qxf2 will live in this repo. Each lambda will have it's own directory. Optionally, each lambda might have one GitHub Action related to it's deploy.

### Context
We are really not sure how to distribute code among repos when maintaining a microservices style of architecture. We use a few AWS lambda functions within Qxf2. As of Juy 2020, they were in the repos that needed them. We moved all the lambdas into one repo to try out how this style of distributing code would work out for us.

#### Prerequisite for running Unit tests and End to End tests
1.Please make sure that you have setup aws credentials of the test account such as `Region`, `Access Key` and `Secret access key` in the `~/.aws/credentials` folder
2.Create sqs queue which is subscribed to `qxf2-skype-listner` SNS topic.
3.Mention the sqs name in the `sqs_utilities_conf.py` file in the `QUEUE_URL_LIST`.
4.Minimum Python version requirement is 3.7+

### How to run End to End tests
Please run the test using command `python tests/test_e2e_employee_skype_message.py`

