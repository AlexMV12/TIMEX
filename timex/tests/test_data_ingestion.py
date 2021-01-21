from datetime import datetime

from pandas._libs.tslibs.timestamps import Timestamp
import pandas as pd
import numpy as np

from timex.data_ingestion.data_ingestion import data_ingestion, add_freq
from timex.tests.utilities import get_fake_df


class TestDataIngestion:
    def test_data_ingestion_univariate_1(self):
        # Local load, with datetime. Infer freq.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1.csv",
                "columns_to_load_from_url": "first_column,third_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                }
            }
        }

        df = data_ingestion(param_config)
        assert df.index.name == "first_column"
        assert df.index.values[0] == Timestamp("2020-02-25")
        assert df.index.values[1] == Timestamp("2020-02-26")
        assert df.index.values[2] == Timestamp("2020-02-27")

        assert df.columns[0] == "third_column"
        assert df.iloc[0]["third_column"] == 3
        assert df.iloc[1]["third_column"] == 6
        assert df.iloc[2]["third_column"] == 9

        assert df.index.freq == '1d'

    def test_data_ingestion_univariate_2(self):
        # Local load, with datetime. Specify freq.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1_1.csv",
                "columns_to_load_from_url": "first_column,third_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                },
                "frequency": "M"
            }
        }

        df = data_ingestion(param_config)
        assert df.index.name == "first_column"
        assert df.index.values[0] == Timestamp("2011-01-31 18:00:00")
        assert df.index.values[1] == Timestamp("2011-02-28 18:00:00")
        assert df.index.values[2] == Timestamp("2011-03-31 18:00:00")

        assert df.columns[0] == "third_column"
        assert df.iloc[0]["third_column"] == 3
        assert df.iloc[1]["third_column"] == 6
        assert df.iloc[2]["third_column"] == 9

        assert df.index.freq == 'M'

    def test_data_ingestion_univariate_3(self):
        # Local load, with no datetime column.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1.csv",
                "columns_to_load_from_url": "second_column,third_column",
                "index_column_name": "second_column"
            }
        }

        df = data_ingestion(param_config)

        assert df.index.name == "second_column"

        assert df.index.values[0] == 2
        assert df.index.values[1] == 5
        assert df.index.values[2] == 8

        assert df.columns[0] == "third_column"
        assert df.iloc[0]["third_column"] == 3
        assert df.iloc[1]["third_column"] == 6
        assert df.iloc[2]["third_column"] == 9

    def test_data_ingestion_univariate_4(self):
        # Local load, with no datetime column. Check columns'order is maintained.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1.csv",
                "columns_to_load_from_url": "third_column,second_column,first_column",
                "index_column_name": "second_column",
            }
        }

        df = data_ingestion(param_config)

        assert df.index.name == "second_column"
        assert df.columns[0] == "third_column"
        assert df.columns[1] == "first_column"

    def test_data_ingestion_univariate_5(self):
        # Local load, with diff columns.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1_2.csv",
                "columns_to_load_from_url": "third_column,second_column,first_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                },
                "add_diff_column": "third_column,second_column"
            }
        }

        df = data_ingestion(param_config)

        assert df.index.name == "first_column"
        assert df.columns[0] == "third_column"
        assert df.columns[1] == "second_column"
        assert df.columns[2] == "third_column_diff"
        assert df.columns[3] == "second_column_diff"
        assert len(df.columns) == 4
        assert len(df) == 3

    def test_data_ingestion_univariate_6(self):
        # Local load, with diff columns. Rename columns.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1_2.csv",
                "columns_to_load_from_url": "third_column,second_column,first_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                },
                "add_diff_column": "third_column,second_column",
                "scenarios_names":
                    {
                        "first_column": "A",
                        "second_column": "B",
                        "third_column": "C",
                        "third_column_diff": "D",
                        "second_column_diff": "E"
                    }
            }
        }

        df = data_ingestion(param_config)

        assert df.index.name == "A"
        assert df.columns[0] == "C"
        assert df.columns[1] == "B"
        assert df.columns[2] == "D"
        assert df.columns[3] == "E"
        assert len(df.columns) == 4
        assert len(df) == 3

    def test_data_ingestion_univariate_7(self):
        # Test that duplicated data is removed.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_4.csv",
                "columns_to_load_from_url": "first_column,second_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                },
            }
        }

        df = data_ingestion(param_config)

        assert len(df) == 3
        assert df.iloc[0, 0] == 1
        assert df.iloc[1, 0] == 3
        assert df.iloc[2, 0] == 4

    def test_data_ingestion_univariate_8(self):
        # Local load, read all columns.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_1.csv",
                "columns_to_load_from_url": "",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "date_formats": ["%Y-%m-%dT%H:%M:%S"]
                }
            }
        }

        df = data_ingestion(param_config)
        assert df.index.name == "first_column"
        assert df.index.values[0] == Timestamp("2020-02-25")
        assert df.index.values[1] == Timestamp("2020-02-26")
        assert df.index.values[2] == Timestamp("2020-02-27")

        assert df.columns[0] == "second_column"
        assert df.iloc[0]["second_column"] == 2
        assert df.iloc[1]["second_column"] == 5
        assert df.iloc[2]["second_column"] == 8

        assert df.columns[1] == "third_column"
        assert df.iloc[0]["third_column"] == 3
        assert df.iloc[1]["third_column"] == 6
        assert df.iloc[2]["third_column"] == 9

        assert df.index.freq == '1d'

    def test_data_ingestion_univariate_9(self):
        # Local load, with datetime with italian months (e.g. Gen, Feb, etc.)
        # Check that monthly freq is applied.
        param_config = {
            "input_parameters": {
                "source_data_url": "test_datasets/test_5.csv",
                "columns_to_load_from_url": "first_column,third_column",
                "datetime_column_name": "first_column",
                "index_column_name": "first_column",
                "dateparser_options": {
                    "settings": { "PREFER_DAY_OF_MONTH": "first" }
                }
            }
        }

        df = data_ingestion(param_config)
        assert df.index.name == "first_column"
        assert df.index.values[0] == Timestamp("2020-11-01")
        assert df.index.values[1] == Timestamp("2020-12-01")
        assert df.index.values[2] == Timestamp("2021-01-01")

        assert df.columns[0] == "third_column"
        assert df.iloc[0]["third_column"] == 3
        assert df.iloc[1]["third_column"] == 6
        assert df.iloc[2]["third_column"] == 9

        assert df.index.freq == 'MS'


class TestAddFreq:
    def test_add_freq_1(self):
        # df already has freq; do nothing.
        df = get_fake_df(10)
        new_df = add_freq(df)

        assert df.equals(new_df)

    def test_add_freq_2(self):
        # df is daily; check if it is set, without passing it.
        df = get_fake_df(10)
        df.index.freq = None

        new_df = add_freq(df)
        assert df.equals(new_df)
        assert new_df.index.freq == "D"

    def test_add_freq_3(self):
        # df is daily; check if it is set, passing it.
        df = get_fake_df(10)
        df.index.freq = None

        new_df = add_freq(df, "D")
        assert df.equals(new_df)
        assert new_df.index.freq == "D"

    def test_add_freq_4(self):
        # df is daily, but with different hours.
        # Check if it is set so.
        dates = [pd.Timestamp(datetime(year=2020, month=1, day=1, hour=10, minute=00)),
                 pd.Timestamp(datetime(year=2020, month=1, day=2, hour=12, minute=21)),
                 pd.Timestamp(datetime(year=2020, month=1, day=3, hour=13, minute=30)),
                 pd.Timestamp(datetime(year=2020, month=1, day=4, hour=11, minute=32))]

        ts = pd.DataFrame(np.random.randn(4), index=dates)

        new_ts = add_freq(ts)
        assert ts.iloc[0].equals(new_ts.iloc[0])
        assert new_ts.index[0] == Timestamp('2020-01-01 00:00:00', freq='D')
        assert new_ts.index[1] == Timestamp('2020-01-02 00:00:00', freq='D')
        assert new_ts.index[2] == Timestamp('2020-01-03 00:00:00', freq='D')
        assert new_ts.index[3] == Timestamp('2020-01-04 00:00:00', freq='D')
        assert new_ts.index.freq == "D"

    def test_add_freq_5(self):
        # df has no clear frequency.
        # Check if it is not set so.
        dates = [pd.Timestamp(datetime(year=2020, month=1, day=1, hour=10, minute=00)),
                 pd.Timestamp(datetime(year=2020, month=1, day=3, hour=12, minute=21)),
                 pd.Timestamp(datetime(year=2020, month=1, day=7, hour=13, minute=30)),
                 pd.Timestamp(datetime(year=2020, month=1, day=19, hour=11, minute=32))]

        ts = pd.DataFrame(np.random.randn(4), index=dates)

        new_ts = add_freq(ts)
        assert new_ts.equals(ts)
        assert new_ts.index.freq == None

