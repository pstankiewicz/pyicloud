from __future__ import absolute_import


class ContactsService(object):
    """
    The 'Contacts' iCloud service, connects to iCloud and returns contacts.
    """

    def __init__(self, service_root, session, params):
        self.session = session
        self.params = params
        self._service_root = service_root
        self._contacts_endpoint = '%s/co' % self._service_root
        self._contacts_refresh_url = '%s/startup' % self._contacts_endpoint
        self._contacts_changeset_url = '%s/changeset' % self._contacts_endpoint

    def refresh_client(self, from_dt=None, to_dt=None):
        """
        Refreshes the ContactsService endpoint, ensuring that the
        contacts data is up-to-date.
        """
        params_contacts = dict(self.params)
        params_contacts.update({
            'clientVersion': '2.1',
            'locale': 'en_US',
            'order': 'last,first',
        })
        req = self.session.get(
            self._contacts_refresh_url,
            params=params_contacts
        )
        self.response = req.json()
        params_refresh = dict(params_contacts)
        params_refresh.update({
            'prefToken': req.json()["prefToken"],
            'syncToken': req.json()["syncToken"],
        })
        self.session.post(self._contacts_changeset_url, params=params_refresh)
        req = self.session.get(
            self._contacts_refresh_url,
            params=params_contacts
        )
        self.response = req.json()

    def all(self):
        """
        Retrieves all contacts.
        """
        self.refresh_client()
        return self.response['contacts']

    def get_all_contacts(self):
        """
        Method returns all contacts. Default all() method
        returns only first 500 contacts.
        Method is implemented based on https://github.com/picklepete/pyicloud/issues/103
        """

        params_contacts = dict(self.params)
        params_contacts.update({
            'clientVersion': '2.1',
            'locale': 'en_US',
            'order': 'last,first',
        })
        req = self.session.get(
            self._contacts_refresh_url,
            params=params_contacts
        )
        self.response = req.json()
        params_refresh = dict(params_contacts)
        params_refresh.update({
            'prefToken': req.json()["prefToken"],
            'syncToken': req.json()["syncToken"],
        })
        self.session.post(self._contacts_changeset_url, params=params_refresh)
        req = self.session.get(
            self._contacts_refresh_url,
            params=params_contacts
        )
        self.response = req.json()

        _contacts_next_url = '%s/contacts' % self._contacts_endpoint
        limit = 500
        params_next = dict(self.params)
        params_next.update({
            'limit': limit,
            'offset': 0,
            'order': 'last,first',
            'clientVersion': '2.1',
            'prefToken': req.json()['prefToken'],
            'syncToken': req.json()['syncToken']
        })
        contacts = []
        while True:
            req = self.session.get(
                _contacts_next_url,
                params=params_next
            )
            self.response = req.json().get('contacts', []) if req.json() else req.json()

            if self.response:
                contacts += self.response
                params_next['offset'] += limit
            if not self.response or len(self.response) < limit:
                break

        return contacts