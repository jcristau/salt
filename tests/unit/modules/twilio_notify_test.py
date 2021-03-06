# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''

# Import Python Libs
from __future__ import absolute_import

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

from salttesting.helpers import ensure_in_syspath

ensure_in_syspath('../../')

# Import Salt Libs
from salt.modules import twilio_notify


class MockTwilioRestException(Exception):
    '''
    Mock TwilioRestException class
    '''
    def __init__(self):
        self.code = 'error code'
        self.msg = 'Exception error'
        self.status = 'Not send'
        super(MockTwilioRestException, self).__init__(self.msg)


class MockMessages(object):
    '''
    Mock SMS class
    '''
    flag = None

    def __init__(self):
        self.sid = '011'
        self.price = '200'
        self.price_unit = '1'
        self.status = 'Sent'
        self.num_segments = '2'
        self.body = None
        self.date_sent = '01-01-2015'
        self.date_created = '01-01-2015'
        self.to = None
        self.from_ = None

    def create(self, body, to, from_):
        '''
        Mock create method
        '''
        msg = MockMessages()
        if self.flag == 1:
            raise MockTwilioRestException()
        msg.body = body
        msg.to = to
        msg.from_ = from_
        return msg


class MockSMS(object):
    '''
    Mock SMS class
    '''
    def __init__(self):
        self.messages = MockMessages()


class MockTwilioRestClient(object):
    '''
    Mock TwilioRestClient class
    '''
    def __init__(self):
        self.sms = MockSMS()

twilio_notify.TwilioRestClient = MockTwilioRestClient
twilio_notify.TwilioRestException = MockTwilioRestException


@skipIf(NO_MOCK, NO_MOCK_REASON)
class TwilioNotifyTestCase(TestCase):
    '''
    Test cases for salt.modules.twilio_notify
    '''
    # 'send_sms' function tests: 1

    def test_send_sms(self):
        '''
        Test if it send an sms.
        '''
        mock = MagicMock(return_value=MockTwilioRestClient())
        with patch.object(twilio_notify, '_get_twilio', mock):
            self.assertDictEqual(twilio_notify.send_sms('twilio-account',
                                                        'SALTSTACK',
                                                        '+18019999999',
                                                        '+18011111111'),
                                 {'message': {'status': 'Sent',
                                              'num_segments': '2',
                                              'price': '200',
                                              'body': 'SALTSTACK', 'sid': '011',
                                              'date_sent': '01-01-2015',
                                              'date_created': '01-01-2015',
                                              'price_unit': '1'}})

            MockMessages.flag = 1
            self.assertDictEqual(twilio_notify.send_sms('twilio-account',
                                                        'SALTSTACK',
                                                        '+18019999999',
                                                        '+18011111111'),
                                 {'message': {'sid': None}, '_error':
                                  {'msg': 'Exception error',
                                   'status': 'Not send', 'code': 'error code'}})


if __name__ == '__main__':
    from integration import run_tests
    run_tests(TwilioNotifyTestCase, needs_daemon=False)
