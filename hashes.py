import os, pathlib
import typing
import hashlib

def get_file_hash(
        filepath: typing.Union[str|pathlib.Path], 
        hash_algo: str = 'sha256'
    ) -> str:
    """
    Docstring for get_file_hash
    
    :param filepath: Absolute path to file to hash
    :type filepath: typing.Union[str | pathlib.Path]
    :param hash_algo: Algorithm used to check hash of file
    :type hash_algo: str
    :return: Hash value of file
    :rtype: str
    """

    hash_func = hashlib.new(hash_algo)

    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()

def compare_file_hashes(
        file1: typing.Union[str|pathlib.Path], 
        file2: typing.Union[str|pathlib.Path], 
        hash_algo='sha256'
    ) -> bool:
    """
    Docstring for compare_file_hashes
    
    :param file1: Absolute path of file 1
    :type file1: typing.Union[str | pathlib.Path]
    :param file2: Absolute path of file 2
    :type file2: typing.Union[str | pathlib.Path]
    :param hash_algo: Algorithm used to check hash of file
    :return: Equality of hashes of the 2 files
    :rtype: bool
    """
    if not os.path.exists(file1) or not os.path.exists(file2):
        return False
    
    return get_file_hash(file1, hash_algo) == get_file_hash(file2, hash_algo)