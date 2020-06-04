import logging
import os
import time
from enum import Enum
from functools import wraps


class RetryDecorator:
    """
    This class is used to retry requests at an API/Web page.
    Use the main method as a decorator on any request call you wish.
    ** Some more testing are required **
    """
    logger = logging.getLogger(__name__)

    @classmethod
    def main(cls, exceptions, total_tries=4, initial_wait=0.5, backoff=2, logger=None):
        """
        calling the decorated function applying an exponential backoff.

        exceptions: Exception(s) that trigger a retry, can be a tuple
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
        """

        def retry_decorator(f):
            @wraps(f)
            def retries(*args, **kwargs):
                tries, delay = total_tries + 1, initial_wait
                while tries > 1:
                    try:
                        cls.log(f'{total_tries + 2 - tries}. try:', logger)
                        return f(*args, **kwargs)
                    except exceptions as e:
                        tries -= 1
                        print_args = args if args else 'no args'
                        if tries == 1:
                            msg = str(f'Function: {f.__name__}\n'
                                      f'Failed despite best efforts after {total_tries} tries.\n'
                                      f'args: {print_args}, kwargs: {kwargs}')
                            cls.log(msg, logger)
                            raise
                        msg = str(f'Function: {f.__name__}\n'
                                  f'Exception: {e}\n'
                                  f'Retrying in {delay} seconds!, args: {print_args}, kwargs: {kwargs}\n')
                        cls.log(msg, logger)
                        time.sleep(delay)
                        delay *= backoff

            return retries
        return retry_decorator

    @classmethod
    def log(cls, msg, logger=None):
        if logger:
            logger.warning(msg)
        print(msg)
        
    def retry_request(exceptions=None, total_retries=3):
    """
    :rtype: Requests retry Decorator Object
    """
    exceptions = exceptions or Exception
    return RetryDecorator.main(exceptions, total_retries=total_retries, logger=RetryDecorator.logger)


def get_file_path(dir_path, name, template):
    """
    @:param template:  file's template (txt,html...)
    @return: The path to the given file.
    @rtype: str
    """
    substring = f'{name}.{template}'
    for path in os.listdir(dir_path):
        full_path = os.path.join(dir_path, path)
        if full_path.endswith(substring):
            return full_path


def repack(data, return_type: str):
    """
    This function receives a list of ordered dictionaries to to unpack and reassign every dict to it's first value.
    data: the data to unpack
    return_type: specify the returned data type, dict of the dictionaries or list them.
    """
    try:
        repacked_dict = {next(iter(d.values())): d for d in data}
        if return_type is 'dict':
            return repacked_dict
        elif return_type is 'list':
            repacked_list = list(repacked_dict.items())
            return repacked_list
        raise TypeError('requested return type is not valid.')
    except:
        raise TypeError('data is not a list.')


def tupled_list(dictionary):
    """
    Takes in a dictionary and repacks it with tuples instead.
    """
    to_be_tuples = list(dictionary.values())
    names = list(dictionary.keys())
    tuples = []
    for di in to_be_tuples:
        tup = tuple(di.values())
        tuples.append(tup)
    return names, tuples


def repack_with_tuple(dictionary) -> dict:
    """
    receives tuples and keys in order to create a new dictionary.
    """
    names, tuples = tupled_list(dictionary)
    end_dict = {k: v for (k, v) in zip(names, tuples)}
    return end_dict


def return_data_by_name(data, query) -> list:
    """
    This function receive a nested dictionary and matches a given query to the keys of the dictionary,
    If there's a match, than that match values are returned.
    :param dict data:
    :param str query:
    """
    for name, values in data.items():
        if query.lower() in name.lower():
            values = list(values.values())
            return values


def sort_ordered_dict(dictionary):
    """
    Takes in a regular dictionary containing nested dictionaries and returns it sorted by the nested dicts values.
    :return sorted_dict = collections.OrderedDict:
    """
    sorted_dict = OrderedDict(
        sorted([[k, v] for (k, v) in dictionary.items()], key=lambda kv: sum(kv[1].values()), reverse=True)
    )
    return sorted_dict        
      
        
        
# Custom Exceptions for The Traingulation calculator, Yet the Class APIException can and sha'll be reused.         
class LocationInfoException(Exception):
    """
    Could not find any locations or missing data about location exception.
    """
    pass


class APIRequestException(Exception):
    """
    Request to API failed.
    """
    pass


class MissionRequestException(Exception):
    """
    Mission File Exception.
    """
    pass


class ElevationException(Exception):
    """
    None/Invalid Elevation value.
    """
    pass


class APIException(Enum):
    """
    Base Exception class for APIs.
    """
    Locations = (205, LocationInfoException, 'No Locations was found or data about location is missing')
    Request = (505, APIRequestException, f'Was not able to get Data from the API')
    Mission = (406,
               MissionRequestException,
               'Mission Was already created. Choose a different name or call the mission ')
    elevation = (515, ElevationException, "This location's Elevation info is either invalid or set to None")

    def __new__(cls, ex_code, ex_class, ex_message):
        # Create New Instance of the exception class
        member = object.__new__(cls)

        member._value_ = ex_code
        member.exception = ex_class
        member.message = ex_message
        return member

    @property
    def code(self):
        return self.value

    def throw(self):
        raise self.exception(f'{self.code} - {self.message}')
