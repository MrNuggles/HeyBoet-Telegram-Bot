# -*- coding: utf-8 -*-

###############################################################################
#
# TaggableFriends
# Returns a list of friends that can be tagged or mentioned in stories published to Facebook.
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

class TaggableFriends(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the TaggableFriends Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(TaggableFriends, self).__init__(temboo_session, '/Library/Facebook/Reading/TaggableFriends')


    def new_input_set(self):
        return TaggableFriendsInputSet()

    def _make_result_set(self, result, path):
        return TaggableFriendsResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return TaggableFriendsChoreographyExecution(session, exec_id, path)

class TaggableFriendsInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the TaggableFriends
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_AccessToken(self, value):
        """
        Set the value of the AccessToken input for this Choreo. ((required, string) The access token retrieved from the final step of the OAuth process.)
        """
        super(TaggableFriendsInputSet, self)._set_input('AccessToken', value)
    def set_After(self, value):
        """
        Set the value of the After input for this Choreo. ((optional, string) A cursor that points to the end of the page of data that has been returned. You can pass this cursor to retrievet he next page of results.)
        """
        super(TaggableFriendsInputSet, self)._set_input('After', value)
    def set_Before(self, value):
        """
        Set the value of the Before input for this Choreo. ((optional, string) A cursor that points to the start of the page of data that has been returned. You can pass this cursor to retrieve the previous page of results.)
        """
        super(TaggableFriendsInputSet, self)._set_input('Before', value)
    def set_Fields(self, value):
        """
        Set the value of the Fields input for this Choreo. ((optional, string) A comma separated list of fields to return (i.e. id,name).)
        """
        super(TaggableFriendsInputSet, self)._set_input('Fields', value)
    def set_Limit(self, value):
        """
        Set the value of the Limit input for this Choreo. ((optional, integer) Limits the number of records returned in the response.)
        """
        super(TaggableFriendsInputSet, self)._set_input('Limit', value)
    def set_ProfileID(self, value):
        """
        Set the value of the ProfileID input for this Choreo. ((optional, string) The id of the profile to retrieve tagged places for. Defaults to "me" indicating the authenticated user.)
        """
        super(TaggableFriendsInputSet, self)._set_input('ProfileID', value)
    def set_ResponseFormat(self, value):
        """
        Set the value of the ResponseFormat input for this Choreo. ((optional, string) The format that the response should be in. Can be set to xml or json. Defaults to json.)
        """
        super(TaggableFriendsInputSet, self)._set_input('ResponseFormat', value)

class TaggableFriendsResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the TaggableFriends Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. (The response from Facebook. Corresponds to the ResponseFormat input. Defaults to JSON.)
        """
        return self._output.get('Response', None)
    def get_HasNext(self):
        """
        Retrieve the value for the "HasNext" output from this Choreo execution. ((boolean) A boolean flag indicating that a next page exists.)
        """
        return self._output.get('HasNext', None)
    def get_HasPrevious(self):
        """
        Retrieve the value for the "HasPrevious" output from this Choreo execution. ((boolean) A boolean flag indicating that a previous page exists.)
        """
        return self._output.get('HasPrevious', None)

class TaggableFriendsChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return TaggableFriendsResultSet(response, path)
