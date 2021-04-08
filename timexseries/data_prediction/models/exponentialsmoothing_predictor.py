import logging
import warnings

from pandas import DataFrame
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller

from timexseries.data_prediction import PredictionModel
import numpy as np
import pandas as pd
import statsmodels.api as sm

log = logging.getLogger(__name__)


class ExponentialSmoothingModel(PredictionModel):
    """
    Exponential smoothing prediction model.
    This model uses the Holt Winters method and automatic parameters estimation.
    """

    def __init__(self, params: dict, transformation: str = None):
        super().__init__(params, name="ExponentialSmoothing", transformation=transformation)
        self.model = None
        self.len_train_set = 0

    def train(self, input_data: DataFrame, extra_regressors: DataFrame = None):
        """Overrides PredictionModel.train()"""

        def isTimeSeriesTrendStationary(timeseries, significance=.05):
            # Dickey-Fuller test:
            adfTest = adfuller(timeseries, autolag='AIC')

            self.pValue = adfTest[1]

            if (self.pValue < significance):
                return True
            else:
                return False

        s = pd.Series(sm.tsa.acf(input_data, nlags=round(len(input_data) / 2 - 1), fft=True))
        s[0] = 0
        s[1] = 0
        s = s.sort_values(ascending=False)

        possible_sp = np.array(s.index[0:10])
        errors = pd.Series([], dtype=np.float64)
        delta_test = int(round(0.1 * len(input_data)))
        train_data = input_data[:-delta_test]
        test_data = input_data[-delta_test:]

        is_stationary = isTimeSeriesTrendStationary(train_data)
        error_function = mean_absolute_error if self.main_accuracy_estimator.upper() == "MAE" else mean_squared_error

        for sp in possible_sp:
            try:
                if is_stationary:
                    model = ExponentialSmoothing(train_data, seasonal="add", initialization_method='estimated',
                                                 seasonal_periods=sp)
                else:
                    model = ExponentialSmoothing(train_data, trend="add", damped_trend=True, seasonal="add",
                                                 initialization_method='estimated', seasonal_periods=sp)

                # fit model
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model_fit = model.fit()

                # make prediction
                yhat_grid = model_fit.predict(start=input_data.index[0], end=input_data.index[-1])
                errors[sp] = error_function(test_data, yhat_grid[-delta_test:])
            except:
                errors[sp] = np.inf

        if is_stationary:
            self.model = ExponentialSmoothing(input_data, seasonal="add", initialization_method='estimated',
                                              seasonal_periods=errors.idxmin())
        else:
            self.model = ExponentialSmoothing(input_data, trend="add", damped_trend=True, seasonal="add",
                                              initialization_method='estimated', seasonal_periods=errors.idxmin())

        self.len_train_set = len(input_data)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model = self.model.fit()

    def predict(self, future_dataframe: DataFrame, extra_regressors: DataFrame = None) -> DataFrame:
        """Overrides PredictionModel.predict()"""
        predictions = self.model.predict(start=future_dataframe.index[0], end=future_dataframe.index[-1])

        future_dataframe.yhat = predictions

        return future_dataframe
