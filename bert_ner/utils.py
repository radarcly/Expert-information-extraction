import torch
import random
import numpy as np 
import os
import time
import pickle
import hashlib
import torch
import logging
from contextlib import contextmanager
__saved_path__ = "saved/vars"

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

@contextmanager
def time_recorder(operation=None):
    start = time.time()
    yield
    end = time.time()
    logging.info("{} cost {:.3} seconds".format(operation if operation else '', end - start))


def check_and_create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def func_cache(cache_dir):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    def cache_decorator(func):
        def wrapper(*args, **kwargs):
            file_name_before_hash = '{}.{}'.format(func.__name__, '_'.join([str(arg) for arg in args]))
            cache_file_name = hashlib.md5(file_name_before_hash.encode('utf8')).hexdigest() + '.pkl'
            cache_file_path = os.path.join(cache_dir, cache_file_name)
            if os.path.exists(cache_file_path) and os.path.isfile(cache_file_path):
                with open(cache_file_path, 'rb') as cache:
                    logging.info('Loading cached result from {}'.format(cache_file_path))
                    return pickle.load(cache)

            result = func(*args, **kwargs)

            with open(cache_file_path, 'wb') as cache:
                pickle.dump(result, cache)
                logging.info('Saving result to cache {}'.format(cache_file_path))
            return result

        return wrapper

    return cache_decorator


def save_var(variable, name, path=None):
    if path is None:
        path = __saved_path__
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    pickle.dump(variable, open("{}/{}.pkl".format(path, name), "wb"))


def load_var(name, path=None):
    if path is None:
        path = __saved_path__
    return pickle.load(open("{}/{}.pkl".format(path, name), "rb"))


def exist_var(name, path=None):
    if path is None:
        path = __saved_path__
    return os.path.exists("{}/{}.pkl".format(path, name))


def auto_create(name, func, cache=False, path=None):
    if path is None:
        path = __saved_path__
    if cache and exist_var(name, path):
        logging.info("cache for {} exists".format(name))
        with time_recorder("*** load {} from cache".format(name)):
            obj = load_var(name, path)
    else:
        logging.info("cache for {} does not exist".format(name))
        with time_recorder("*** create {} and save to cache".format(name)):
            obj = func()
            save_var(obj, name, path)
    return obj

# 判断一个字符是不是英文字符
def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False

# 判断一个字符是不是数字
def is_number(uchar):
    """判断一个unicode是否是数字"""
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False

# 判断一个字符串是否是int
def str_is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

# 判断一个字符是不是汉字
def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if  u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False

# 判断一个字符是不是空格
def is_space(uchar):
    """判断一个unicode是否是空字符串（包括空格，回车，tab）"""
    space = [u'\u0020', u'\u000A', u'\u000D', u'\u0009']
    if uchar in space:
        return True
    else:
        return False

# 判断一个字符是否非汉字，数字，空字符和英文字符
def is_other(uchar):
    """判断是否非汉字，数字，空字符和英文字符"""
    if not (is_space(uchar) or is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

# 判断一个字符串是不是英文字符串，如果一个字符串英文字符长度是中文字符长度5倍就认为他是英文字符串
def is_english(str):
    e_num = 0
    c_num =0
    for ch in str:
        if is_alphabet(ch):
            e_num += 1
        elif is_chinese(ch):
            c_num += 1
    if e_num > 5*c_num:
        return True
    else:
        return False

