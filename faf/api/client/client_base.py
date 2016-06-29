import json

from abc import abstractmethod
from faf.api import API_TYPES, FAF_API_URL


class ApiException(Exception):
    def __init__(self, message, inner=None):
        Exception.__init__(self, message, inner)


class BaseApiClient:
    """
    Base class for synchronous FAF api clients.
    """

    def __init__(self):
        """
        Initialize an ApiClient
        :return:
        """
        self._session = self.make_session()
        self._base_url = FAF_API_URL
        self._headers = {'Content-Type': 'application/vnd.api+json'}

    @abstractmethod
    def make_session(self):
        """
        Implementors override this to create a session object resembling requests.Session
        :return: session object
        :rtype: requests.Session
        """
        pass

    def deserialize_obj(self, obj):
        first = obj.get('data', {})
        if isinstance(first, list):
            many = True
        elif isinstance(first, dict):
            many = False
        else:
            raise ApiException("Unknown Data Format")

        if many:
            type_ = first[0].get('type', None)
        else:
            type_ = first.get('type', None)
        schema = API_TYPES.get(type_)()
        result, errors = schema.load(obj, many=True)
        if errors:
            raise ApiException(errors)
        return result

    def get(self, url, **kwargs):
        """
        Retrieve and deserialize the objects at the given url

        :param url: url to retrieve
        :param kwargs: additional arguments to be passed to the underlying implementation

        :return: A set of objects deserialized according to the schema
        """
        response = self._session.get(self._base_url + url, headers=self._headers)
        decoded = json.loads(response.content.decode('utf-8'))
        return self.deserialize_obj(decoded)

    def post(self, url, **kwargs):
        """
        Serialize and POST the given objects to the given url
        :param url: url to POST to
        :param kwargs: arguments for the underlying implementation
        :return: response object
        """
        return self._session.post(self._base_url + url, **kwargs)

    def put(self, url, **kwargs):
        """
        Serialize and PUT the given objects to the given url
        :param url: url to POST to
        :param data: objects to send
        :param kwargs: arguments for the underlying implementation
        :return: response object
        """
        return self._session.put(self._base_url + url, **kwargs)

    def delete(self, url, **kwargs):
        """
        Delete the object at the given url
        :param url: url to send DELETE to
        :param kwargs: additional arguments to the underlying implementation
        :return: response object
        """
        return self._session.delete(self._base_url + url, **kwargs)
