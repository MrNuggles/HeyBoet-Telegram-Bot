# -*- coding: utf-8 -*-

###############################################################################
#
# DeleteTicket
# Deletes an existing ticket.
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

class DeleteTicket(Choreography):

    def __init__(self, temboo_session):
        """
        Create a new instance of the DeleteTicket Choreo. A TembooSession object, containing a valid
        set of Temboo credentials, must be supplied.
        """
        super(DeleteTicket, self).__init__(temboo_session, '/Library/Zendesk/Tickets/DeleteTicket')


    def new_input_set(self):
        return DeleteTicketInputSet()

    def _make_result_set(self, result, path):
        return DeleteTicketResultSet(result, path)

    def _make_execution(self, session, exec_id, path):
        return DeleteTicketChoreographyExecution(session, exec_id, path)

class DeleteTicketInputSet(InputSet):
    """
    An InputSet with methods appropriate for specifying the inputs to the DeleteTicket
    Choreo. The InputSet object is used to specify input parameters when executing this Choreo.
    """
    def set_Email(self, value):
        """
        Set the value of the Email input for this Choreo. ((required, string) The email address you use to login to your Zendesk account.)
        """
        super(DeleteTicketInputSet, self)._set_input('Email', value)
    def set_ID(self, value):
        """
        Set the value of the ID input for this Choreo. ((required, integer) The ID number of a ticket.)
        """
        super(DeleteTicketInputSet, self)._set_input('ID', value)
    def set_Password(self, value):
        """
        Set the value of the Password input for this Choreo. ((required, password) Your Zendesk password.)
        """
        super(DeleteTicketInputSet, self)._set_input('Password', value)
    def set_Server(self, value):
        """
        Set the value of the Server input for this Choreo. ((required, string) Your Zendesk domain and subdomain (e.g., temboocare.zendesk.com).)
        """
        super(DeleteTicketInputSet, self)._set_input('Server', value)

class DeleteTicketResultSet(ResultSet):
    """
    A ResultSet with methods tailored to the values returned by the DeleteTicket Choreo.
    The ResultSet object is used to retrieve the results of a Choreo execution.
    """

    def getJSONFromString(self, str):
        return json.loads(str)

    def get_Response(self):
        """
        Retrieve the value for the "Response" output from this Choreo execution. ((json) The response from Zendesk.)
        """
        return self._output.get('Response', None)
    def get_ResponseStatusCode(self):
        """
        Retrieve the value for the "ResponseStatusCode" output from this Choreo execution. ((integer) The response status code returned from Zendesk.)
        """
        return self._output.get('ResponseStatusCode', None)

class DeleteTicketChoreographyExecution(ChoreographyExecution):

    def _make_result_set(self, response, path):
        return DeleteTicketResultSet(response, path)
