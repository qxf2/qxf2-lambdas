"""
Code level tests for get_message_contents method pf pto_detector lambda
"""
import ast
import collections
from parameterized import parameterized, parameterized_class
from pto_detector import pto_detector

def get_class_name(cls, num, params_dict):
    """
    multiple parameters being included in the generated class name:
    """
    return "%s_%s_%s%s" %(
        cls.__name__,
        num,
        parameterized.to_safe_name(params_dict['event']),
        parameterized.to_safe_name(params_dict['expected_message_contents']),
    )

@parameterized_class([
   { "event":str({"Records": [{"body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am on PTO today\\\", \\\"chat_id\\\": \\\"19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"}]}), "expected_message_contents": str({'msg': 'Test: I am on PTO today', 'chat_id': '19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype','user_id': 'blah'})},
   { "event":str({"Records": [{"body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am on PTO tomorrow\\\", \\\"chat_id\\\": \\\"19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"}]}), "expected_message_contents": str({'msg': 'Test: I am on PTO tomorrow', 'chat_id': '19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype','user_id': 'blah'})}
   ], class_name_func=get_class_name)

class TestWriteMessage(object):
    """
    Test class for get message contents
    """
    def get_event_data_structure(self, event_string):
        """
        Method used for converting nested dictionary/list to data similar to tabular form
        """
        obj = collections.OrderedDict()
        def recurse(dataobject,parent_key=""):
            """
            Method will recurse through object
            """
            if isinstance(dataobject,list):
                # loop through list and call recurse()
                for i in range(len(dataobject)):
                    recurse(dataobject[i],parent_key + "_" + str(i) if parent_key else str(i))
            elif isinstance(dataobject,dict):
                # loop through dictionary and call recurse()
                for key,value in dataobject.items():
                    recurse(value,parent_key + "_" + key if parent_key else key)
            else:
                # use the parent_key and store the value to obj
                obj[parent_key] = dataobject

        recurse(event_string)

        return obj

    def extract_event_from_event_string(self):
        """
        Method to get event dict
        """
        event_structure = self.get_event_data_structure(self.event)
        event =ast.literal_eval(event_structure[''])

        return event

    def test_pto_detector_get_message_contents(self):
        """
        Code level test for pto_detctor
        """
        event = self.extract_event_from_event_string()
        actual_message = pto_detector.get_message_contents(event)
        assert str(actual_message) == self.expected_message_contents
