# -*- coding: utf-8 -*-

###############################################################################
#
# LatestTweet
# Retrieves the latest Tweet matching a specified query.
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

class LatestTweet(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the LatestTweet Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(LatestTweet, self).__init__(temboo_session, '/Library/Twitter/Search/LatestTweet')


    def new_input_set(self):
        return LatestTweetInputSet()

    def _make_result_set(self, result, path):
        return LatestTweetResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return LatestTweetChoreographyExecution(session, exec_id, path)

class LatestTweetInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the LatestTweet
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_AccessTokenSecret(self, value):
        """
        Set the value of the AccessTokenSecret input for this Choreo. ((required, string) The Access Token Secret provided by Twitter or retrieved during the OAuth process.)
        """
        super(LatestTweetInputSet, self)._set_input('AccessTokenSecret', value)
    def set_AccessToken(self, value):
        """
        Set the value of the AccessToken input for this Choreo. ((required, string) The Access Token provided by Twitter or retrieved during the OAuth process.)
        """
        super(LatestTweetInputSet, self)._set_input('AccessToken', value)
    def set_ConsumerKey(self, value):
        """
        Set the value of the ConsumerKey input for this Choreo. ((required, string) The API Key (or Consumer Key) provided by Twitter.)
        """
        super(LatestTweetInputSet, self)._set_input('ConsumerKey', value)
    def set_ConsumerSecret(self, value):
        """
        Set the value of the ConsumerSecret input for this Choreo. ((required, string) The API Secret (or Consumer Secret) provided by Twitter.)
        """
        super(LatestTweetInputSet, self)._set_input('ConsumerSecret', value)
    def set_Geocode(self, value):
        """
        Set the value of the Geocode input for this Choreo. ((optional, string) Returns tweets by users located within a given radius of the given latitude/longitude. Formatted like: 37.781157,-122.398720,1mi.)
        """
        super(LatestTweetInputSet, self)._set_input('Geocode', value)
    def set_IncludeEntities(self, value):
        """
        Set the value of the IncludeEntities input for this Choreo. ((optional, boolean) The "entities" node containing extra metadata will not be included when set to false.)
        """
        super(LatestTweetInputSet, self)._set_input('IncludeEntities', value)
    def set_Language(self, value):
        """
        Set the value of the Language input for this Choreo. ((optional, string) Restricts tweets to the given language, given by an ISO 639-1 code.)
        """
        super(LatestTweetInputSet, self)._set_input('Language', value)
    def set_MaxId(self, value):
        """
        Set the value of the MaxId input for this Choreo. ((optional, string) Returns results with an ID less than (older than) or equal to the specified ID.)
        """
        super(LatestTweetInputSet, self)._set_input('MaxId', value)
    def set_Query(self, value):
        """
        Set the value of the Query input for this Choreo. ((required, string) A search query of up to 1,000 characters.)
        """
        super(LatestTweetInputSet, self)._set_input('Query', value)
    def set_ResultType(self, value):
        """
        Set the value of the ResultType input for this Choreo. ((optional, string) Specifies what type of search results you want to receive. The default is "mixed." Valid values are: mixed, recent, and popular.)
        """
        super(LatestTweetInputSet, self)._set_input('ResultType', value)
    def set_SinceId(self, value):
        """
        Set the value of the SinceId input for this Choreo. ((optional, string) Returns results with an ID greater than (more recent than) the specified ID.)
        """
        super(LatestTweetInputSet, self)._set_input('SinceId', value)
    def set_Until(self, value):
        """
        Set the value of the Until input for this Choreo. ((optional, date) Returns tweets generated before the given date. Date should be formatted as YYYY-MM-DD.)
        """
        super(LatestTweetInputSet, self)._set_input('Until', value)

class LatestTweetResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the LatestTweet Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. ((json) The response from Twitter.)
        """
        return self._output.get('Response', None)
    def get_ID(self):
        """
        Retrieve the value for the "ID" output from this Choreo execution. ((string) The Tweet ID.)
        """
        return self._output.get('ID', None)
    def get_Limit(self):
        """
        Retrieve the value for the "Limit" output from this Choreo execution. ((integer) The rate limit ceiling for this particular request.)
        """
        return self._output.get('Limit', None)
    def get_Remaining(self):
        """
        Retrieve the value for the "Remaining" output from this Choreo execution. ((integer) The number of requests left for the 15 minute window.)
        """
        return self._output.get('Remaining', None)
    def get_Reset(self):
        """
        Retrieve the value for the "Reset" output from this Choreo execution. ((date) The remaining window before the rate limit resets in UTC epoch seconds.)
        """
        return self._output.get('Reset', None)
    def get_ScreenName(self):
        """
        Retrieve the value for the "ScreenName" output from this Choreo execution. ((string) The screen name of the user who posted this Tweet.)
        """
        return self._output.get('ScreenName', None)
    def get_Text(self):
        """
        Retrieve the value for the "Text" output from this Choreo execution. ((string) The Tweet text.)
        """
        return self._output.get('Text', None)

class LatestTweetChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return LatestTweetResultSet(response, path)
