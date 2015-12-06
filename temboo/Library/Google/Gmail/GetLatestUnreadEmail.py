# -*- coding: utf-8 -*-

###############################################################################
#
# GetLatestUnreadEmail
# Returns the latest unread email from a user's Gmail feed.
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

class GetLatestUnreadEmail(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the GetLatestUnreadEmail Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(GetLatestUnreadEmail, self).__init__(temboo_session, '/Library/Google/Gmail/GetLatestUnreadEmail')


    def new_input_set(self):
        return GetLatestUnreadEmailInputSet()

    def _make_result_set(self, result, path):
        return GetLatestUnreadEmailResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return GetLatestUnreadEmailChoreographyExecution(session, exec_id, path)

class GetLatestUnreadEmailInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the GetLatestUnreadEmail
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_AccessToken(self, value):
        """
        Set the value of the AccessToken input for this Choreo. ((optional, string) A valid Access Token retrieved during the OAuth process. This is required unless you provide the ClientID, ClientSecret, and RefreshToken to generate a new Access Token.)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('AccessToken', value)
    def set_ClientID(self, value):
        """
        Set the value of the ClientID input for this Choreo. ((conditional, string) The Client ID provided by Google. Required unless providing a valid AccessToken.)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('ClientID', value)
    def set_ClientSecret(self, value):
        """
        Set the value of the ClientSecret input for this Choreo. ((conditional, string) The Client Secret provided by Google. Required unless providing a valid AccessToken.)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('ClientSecret', value)
    def set_Label(self, value):
        """
        Set the value of the Label input for this Choreo. ((optional, string) The name of a Gmail Label to retrieve messages from (e.g., important, starred, sent, junk-e-mail, all).)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('Label', value)
    def set_Password(self, value):
        """
        Set the value of the Password input for this Choreo. ((optional, password) A Google App-specific password that you've generated after enabling 2-Step Verification (Note: authenticating with OAuth credentials is the preferred authentication method).)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('Password', value)
    def set_RefreshToken(self, value):
        """
        Set the value of the RefreshToken input for this Choreo. ((conditional, string) An OAuth Refresh Token used to generate a new Access Token when the original token is expired. Required unless providing a valid AccessToken.)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('RefreshToken', value)
    def set_ResponseFormat(self, value):
        """
        Set the value of the ResponseFormat input for this Choreo. ((optional, string) The format for the response. Valid values are JSON and XML. This will be ignored when providng an XPath query because results are returned as a string or JSON depending on the Mode specified.)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('ResponseFormat', value)
    def set_Username(self, value):
        """
        Set the value of the Username input for this Choreo. ((optional, string) Your full Google email address e.g., martha.temboo@gmail.com (Note: authenticating with OAuth credentials is the preferred authentication method).)
        """
        super(GetLatestUnreadEmailInputSet, self)._set_input('Username', value)

class GetLatestUnreadEmailResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the GetLatestUnreadEmail Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. (The response from Google. This will contain the data from the Gmail feed, or if the XPath input is provided, it will contain the result of the XPath query.)
        """
        return self._output.get('Response', None)
    def get_AuthorEmail(self):
        """
        Retrieve the value for the "AuthorEmail" output from this Choreo execution. ((string) The author's email address.)
        """
        return self._output.get('AuthorEmail', None)
    def get_AuthorName(self):
        """
        Retrieve the value for the "AuthorName" output from this Choreo execution. ((string) The author's name.)
        """
        return self._output.get('AuthorName', None)
    def get_MessageBody(self):
        """
        Retrieve the value for the "MessageBody" output from this Choreo execution. ((string) The email body. Note that this corresponds to the "summary" element in the feed.)
        """
        return self._output.get('MessageBody', None)
    def get_NewAccessToken(self):
        """
        Retrieve the value for the "NewAccessToken" output from this Choreo execution. ((string) Contains a new AccessToken when the RefreshToken is provided.)
        """
        return self._output.get('NewAccessToken', None)
    def get_Subject(self):
        """
        Retrieve the value for the "Subject" output from this Choreo execution. ((string) The subject line of the email. Note that this corresponds to the "title" element in the feed.)
        """
        return self._output.get('Subject', None)

class GetLatestUnreadEmailChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return GetLatestUnreadEmailResultSet(response, path)
