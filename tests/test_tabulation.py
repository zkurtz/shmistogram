import numpy as np
import pandas as pd

from shmistogram.tabulation import tabulate


def test_tabulate():
    # Define a series of categorical data
    data = ["a", "a", "b", "c", "c", "c", None, None, None]
    series = pd.Series(data).astype("category")
    st = tabulate(series)

    expected_table = pd.DataFrame({"n_obs": {"a": 2, "b": 1, "c": 3, np.nan: 3}})
    expected_table.index = expected_table.index.astype("category")
    pd.testing.assert_frame_equal(st.df, expected_table)
    assert st.name is None

    # If the input series has a name, it should be used as the name of the table
    series.name = "my_series"
    st = tabulate(series)
    assert st.name == "my_series"
