import types
import marshal
import pickle
import base64
import zlib


def _dump_codes(libraries, called_name_as_method, arg, kwargs, stored_funcs, chrome_options):
    dumped_funcs = {name: marshal.dumps(
        func.__code__) for name, func in stored_funcs.items()}
    pickled_data = pickle.dumps((libraries, called_name_as_method, arg,
                                 kwargs, dumped_funcs, chrome_options))
    compressed_data = zlib.compress(pickled_data)
    base64str_data = base64.b64encode(compressed_data).decode()
    return base64str_data


def _unpickle_result(base64str_data):
    try:
        return pickle.loads(zlib.decompress(base64.b64decode(base64str_data.encode())))
    except Exception as e:
        # '{"message": "Internal server error"}'
        # '{"message": "Endpoint request timed out"}'
        raise Exception(
            f"lambda returned {base64str_data}. please check CloudWatch and capacity of lambda is enough.")


if __name__ == '__main__':
    test()
