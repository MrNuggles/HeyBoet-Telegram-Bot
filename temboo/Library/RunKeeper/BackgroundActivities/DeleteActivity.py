# -*- coding: utf-8 -*-

###############################################################################
#
# DeleteActivity
# Removes an individual background activity from a user’s feed.
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

class DeleteActivity(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the DeleteActivity Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(DeleteActivity, self).__init__(temboo_session, '/Library/RunKeeper/BackgroundActivities/DeleteActivity')


    def new_input_set(self):
        return DeleteActivityInputSet()

    def _make_result_set(self, result, path):
        return DeleteActivityResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return DeleteActivityChoreographyExecution(session, exec_id, path)

class DeleteActivityInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the DeleteActivity
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_AccessToken(self, value):
        """
        Set the value of the AccessToken input for this Choreo. ((required, string) The Access Token retrieved after the final step in the OAuth process.)
        """
        super(DeleteActivityInputSet, self)._set_input('AccessToken', value)
    def set_ActivityID(self, value):
        """
        Set the value of the ActivityID input for this Choreo. ((required, string) This can be the individual id of the activity, or you can pass the full uri for the activity as returned from the RetrieveActivities Choreo (i.e. /backgroundActivities/-12985593-1347998400000).)
        """
        super(DeleteActivityInputSet, self)._set_input('ActivityID', value)

class DeleteActivityResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the DeleteActivity Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. ((boolean) Contains the string "true" when activities are successfully deleted.)
        """
        return self._output.get('Response', None)

class DeleteActivityChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return DeleteActivityResultSet(response, path)
