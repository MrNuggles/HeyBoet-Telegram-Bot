# -*- coding: utf-8 -*-

###############################################################################
#
# InboxFeed
# Allows you to access a read-only Gmail feed that contains a list of unread emails.
#
# Python versions 2.6, 2.7, 3.x
#
# Copyright 2014, Temboo Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
#
#
###############################################################################

from temboo.core.choreography import Choreography
from temboo.core.choreography import InputSet
from temboo.core.choreography import ResultSet
from temboo.core.choreography import ChoreographyExecution

import json

class InboxFeed(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the InboxFeed Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(InboxFeed, self).__init__(temboo_session, '/Library/Google/Gmail/InboxFeed')


    def new_input_set(self):
        return InboxFeedInputSet()

    def _make_result_set(self, result, path):
        return InboxFeedResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return InboxFeedChoreographyExecution(session, exec_id, path)

class InboxFeedInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the InboxFeed
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_AccessToken(self, value):
        """
        Set the value of the AccessToken input for this Choreo. ((optional, string) A valid Access Token retrieved during the OAuth process. This is required unless you provide the ClientID, ClientSecret, and RefreshToken to generate a new Access Token.)
        """
        super(InboxFeedInputSet, self)._set_input('AccessToken', value)
    def set_ClientID(self, value):
        """
        Set the value of the ClientID input for this Choreo. ((conditional, string) The Client ID provided by Google. Required unless providing a valid AccessToken.)
        """
        super(InboxFeedInputSet, self)._set_input('ClientID', value)
    def set_ClientSecret(self, value):
        """
        Set the value of the ClientSecret input for this Choreo. ((conditional, string) The Client Secret provided by Google. Required unless providing a valid AccessToken.)
        """
        super(InboxFeedInputSet, self)._set_input('ClientSecret', value)
    def set_Label(self, value):
        """
        Set the value of the Label input for this Choreo. ((optional, string) The name of a Gmail Label to retrieve messages from (e.g., important, starred, sent, junk-e-mail, all).)
        """
        super(InboxFeedInputSet, self)._set_input('Label', value)
    def set_Mode(self, value):
        """
        Set the value of the Mode input for this Choreo. ((optional, string) Used when an XPath query is provided. Valid values are "select" or "recursive". Select mode will return the first match of the query. In recursive mode, the XPath query will be applied within a loop.)
        """
        super(InboxFeedInputSet, self)._set_input('Mode', value)
    def set_Password(self, value):
        """
        Set the value of the Password input for this Choreo. ((optional, password) A Google App-specific password that you've generated after enabling 2-Step Verification (Note: authenticating with OAuth credentials is the preferred authentication method).)
        """
        super(InboxFeedInputSet, self)._set_input('Password', value)
    def set_RefreshToken(self, value):
        """
        Set the value of the RefreshToken input for this Choreo. ((conditional, string) An OAuth Refresh Token used to generate a new Access Token when the original token is expired. Required unless providing a valid AccessToken.)
        """
        super(InboxFeedInputSet, self)._set_input('RefreshToken', value)
    def set_ResponseFormat(self, value):
        """
        Set the value of the ResponseFormat input for this Choreo. ((optional, string) The format for the response. Valid values are JSON and XML. This will be ignored when providng an XPath query because results are returned as a string or JSON depending on the Mode specified.)
        """
        super(InboxFeedInputSet, self)._set_input('ResponseFormat', value)
    def set_Username(self, value):
        """
        Set the value of the Username input for this Choreo. ((optional, string) Your full Google email address e.g., martha.temboo@gmail.com (Note: authenticating with OAuth credentials is the preferred authentication method).)
        """
        super(InboxFeedInputSet, self)._set_input('Username', value)
    def set_XPath(self, value):
        """
        Set the value of the XPath input for this Choreo. ((optional, string) An XPATH query to run.)
        """
        super(InboxFeedInputSet, self)._set_input('XPath', value)

class InboxFeedResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the InboxFeed Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. (The response from Google. This will contain the data from the Gmail feed, or if the XPath input is provided, it will contain the result of the XPath query.)
        """
        return self._output.get('Response', None)
    def get_FullCount(self):
        """
        Retrieve the value for the "FullCount" output from this Choreo execution. ((integer) The number of unread messages. This is parsed from the Google XML response. Note that when using the Label input to retrieve messages from a particular Gmail label, the full count element may be 0.)
        """
        return self._output.get('FullCount', None)
    def get_NewAccessToken(self):
        """
        Retrieve the value for the "NewAccessToken" output from this Choreo execution. ((string) Contains a new AccessToken when the RefreshToken is provided.)
        """
        return self._output.get('NewAccessToken', None)

class InboxFeedChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return InboxFeedResultSet(response, path)
