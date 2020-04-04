
import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np

pd.set_option('display.max_columns', 10)


class DfCompare(object):
    def __init__(self):

        self.today = datetime.today().strftime("%Y%m%d")
        self.yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")

        self.file_new = '/Users/xian.chen/Dropbox/Repo/csrc_tracking/parsed_result/{}_csrc_mutual_fund_application.xls'.format(self.today)
        self.file_old = '/Users/xian.chen/Dropbox/Repo/csrc_tracking/parsed_result/{}_csrc_mutual_fund_application.xls'.format(self.yesterday)

        self.df_old = pd.read_excel(self.file_old, index_col=0)
        self.df_new = pd.read_excel(self.file_new, index_col=0)

    def detect_update(self):
        """
        either new application or status update for existing ones
        """

        common = self.df_new.merge(self.df_old, on=['申请事项名称', '申请日期'], how='inner')
        new_application = self.df_new[(~self.df_new['申请事项名称'].isin(common['申请事项名称'])) & (~self.df_new['申请日期'].isin(common['申请日期']))]

        common.index = np.arange(len(new_application)+1, len(self.df_new) + 1)
        existing_updates = common[~(common['更新进度_x'] == common['更新进度_y'])][['申请事项名称', '更新日期_x', '更新进度_x', '进度跟踪_x']]
        existing_updates = existing_updates.rename(columns={'更新日期_x': '更新日期', '更新进度_x': '更新进度', '进度跟踪_x': '进度跟踪'})

        return new_application, existing_updates


if __name__ == "__main__":
    # old = 'test/20200402_csrc_mutual_fund_application.xls'
    # new = 'test/20200403_csrc_mutual_fund_application.xls'
    df_compare = DfCompare()

    new_application, existing_updates = df_compare.detect_update()
    print(new_application, existing_updates)
