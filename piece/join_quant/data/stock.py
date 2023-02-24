from jqdatasdk import *
import os
JQ_PHONE = os.getenv('JQ_PHONE')
JQ_PWD = os.getenv('JQ_PWD')

auth(JQ_PHONE, JQ_PWD)

df = get_price(['IC1505.CCFX', 'IC1506.CCFX'], start_date='2015-05-06',
               end_date='2015-05-08')  # 获取IC1506.CCFX的2015年的按天数据
print(df)
df = get_price('IC1506.CCFX', start_date='2015-05-06', end_date='2015-05-08', frequency='minute',
               fields=['open', 'close'])  # 获得IC1506.CCFX的分钟数据, 只获取open+close字段

# 获取多只期货
panel = get_price(['IC1505.CCFX', 'IC1506.CCFX'], start_date='2015-05-06',
                  end_date='2015-05-08')  # 获取中IC1505和IC1506的天数据, 返回一个[pandas.Panel]
df_open = panel['open']  # 获取开盘价的[pandas.DataFrame],  行索引是[datetime.datetime]对象, 列索引是期货代号
df_volume = panel['volume']  # 获取交易量的[pandas.DataFrame]
