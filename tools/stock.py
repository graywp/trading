import pandas as pd
from jqdatasdk import *
import datetime
import time
import os

JQ_PHONE = os.getenv('JQ_PHONE')
JQ_PWD = os.getenv('JQ_PWD')

auth(JQ_PHONE, JQ_PWD)

# Set pandas display row and column
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)

data_root = os.path.realpath(__file__).split('trading')[0] + 'trading/output'
print(f'Data root path: {data_root}')


def init_db(skip_exists=True, fetch_interval_millis=100):
    """
    init all stock
    :param skip_exists whether skip when exists
    :param fetch_interval_millis sleep millis between fetches
    :return:
    """
    stocks = get_stock_list()
    data_type = 'price'
    for code in stocks:
        if skip_exists and file_exists(code, data_type):
            continue
        df = get_single_price(code, 'daily')
        save_data(df, code, data_type)
        print(f'{code}: {df.head()}')
        time.sleep(fetch_interval_millis / 1000)


def get_stock_list():
    """
    Get all the stock in China
    Shang hai: .XSHG
    Shen zhen: .XSHE
    :return: stock list
    """
    return list(get_all_securities(['stock']).index)


def get_single_price(code, time_freq, start_date=None, end_date=None):
    """
    get code price
    :param code: stock code
    :param time_freq: time frequency
    :param start_date: start date
    :param end_date: end date
    :return: price info
    """
    if start_date is None:
        # default starts on the date of listings
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    return get_price(code, start_date=start_date, end_date=end_date, frequency=time_freq, panel=False)


def save_data(data: pd.DataFrame, filename, data_type, mode='w'):
    """
    Export stock to database
    :param data: pandas dataframe
    :param filename: save filename
    :param data_type: stock type, such as "price", "finance"
    :param mode: a is for append, w is for write
    :return:
    """
    # check folder exists
    folder = _folder_with_type(data_type)
    if not os.path.exists(folder):
        os.mkdir(folder)
    file_path = _filepath_with_type(filename, data_type)
    data.index.names = ['date']
    if mode == 'a':
        data.to_csv(file_path, mode=mode, header=False)
        # delete the duplicated data
        data_from_file = pd.read_csv(file_path)
        data_from_file.drop_duplicates(subset=['date'])  # according by date
        data_from_file.to_csv(file_path, index=False)
    else:
        data.to_csv(file_path)
    print(f'Save data success: {file_path}')


def file_exists(filename, data_type):
    """
    check file exists
    :param filename:
    :param data_type:
    :return: Bool
    """
    return os.path.exists(_filepath_with_type(filename, data_type))


def get_single_valuation(stock_code, date, stat_date):
    """
    get valuation of stock
    :param stock_code: stock code
    :param date:
    :param stat_date:
    :return:
    """
    return get_fundamentals(query(valuation).filter(valuation.code == stock_code), date=date, statDate=stat_date)


def calculate_change_pct(data):
    """
    change percent = (close_price - last_close_price) / last_close_price
    :param data: pd.DataFrame with column ["close"]
    :return: pd.DataFrame with column ["close_pct"]
    """
    data['close_pct'] = (data['close'] - data['close'].shift(1)) / data['close'].shift(1)
    return data


def update_daily_price(stock_code, data_type='price'):
    """

    :param stock_code:
    :param data_type:
    :return:
    """
    file_path = _filepath_with_type(stock_code, data_type)
    if os.path.exists(file_path):
        start_date = pd.read_csv(file_path, usecols=['date'])['date'].iloc[-1]
        df = get_single_price(stock_code, 'daily', start_date=start_date, end_date=datetime.datetime.today())
        save_data(df, stock_code, 'price', 'a')
    else:
        df = get_single_price(stock_code, 'daily')
        save_data(df, stock_code, 'price')
    print(f'Stock price update success: {stock_code}')


def _filepath_with_type(filename, data_type, suffix='.csv'):
    return data_root + '/' + data_type + '/' + filename + suffix


def _folder_with_type(data_type):
    return data_root + '/' + data_type


if __name__ == '__main__':
    init_db()
