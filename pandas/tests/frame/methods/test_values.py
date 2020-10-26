import numpy as np

from pandas import DataFrame, NaT, Timestamp, date_range
import pandas._testing as tm


class TestDataFrameValues:
    def test_values_duplicates(self):
        df = DataFrame(
            [[1, 2, "a", "b"], [1, 2, "a", "b"]], columns=["one", "one", "two", "two"]
        )

        result = df.values
        expected = np.array([[1, 2, "a", "b"], [1, 2, "a", "b"]], dtype=object)

        tm.assert_numpy_array_equal(result, expected)

    def test_frame_values_with_tz(self):
        tz = "US/Central"
        df = DataFrame({"A": date_range("2000", periods=4, tz=tz)})
        result = df.values
        expected = np.array(
            [
                [Timestamp("2000-01-01", tz=tz)],
                [Timestamp("2000-01-02", tz=tz)],
                [Timestamp("2000-01-03", tz=tz)],
                [Timestamp("2000-01-04", tz=tz)],
            ]
        )
        tm.assert_numpy_array_equal(result, expected)

        # two columns, homogenous

        df["B"] = df["A"]
        result = df.values
        expected = np.concatenate([expected, expected], axis=1)
        tm.assert_numpy_array_equal(result, expected)

        # three columns, heterogeneous
        est = "US/Eastern"
        df["C"] = df["A"].dt.tz_convert(est)

        new = np.array(
            [
                [Timestamp("2000-01-01T01:00:00", tz=est)],
                [Timestamp("2000-01-02T01:00:00", tz=est)],
                [Timestamp("2000-01-03T01:00:00", tz=est)],
                [Timestamp("2000-01-04T01:00:00", tz=est)],
            ]
        )
        expected = np.concatenate([expected, new], axis=1)
        result = df.values
        tm.assert_numpy_array_equal(result, expected)

    def test_interleave_with_tzaware(self, timezone_frame):

        # interleave with object
        result = timezone_frame.assign(D="foo").values
        expected = np.array(
            [
                [
                    Timestamp("2013-01-01 00:00:00"),
                    Timestamp("2013-01-02 00:00:00"),
                    Timestamp("2013-01-03 00:00:00"),
                ],
                [
                    Timestamp("2013-01-01 00:00:00-0500", tz="US/Eastern"),
                    NaT,
                    Timestamp("2013-01-03 00:00:00-0500", tz="US/Eastern"),
                ],
                [
                    Timestamp("2013-01-01 00:00:00+0100", tz="CET"),
                    NaT,
                    Timestamp("2013-01-03 00:00:00+0100", tz="CET"),
                ],
                ["foo", "foo", "foo"],
            ],
            dtype=object,
        ).T
        tm.assert_numpy_array_equal(result, expected)

        # interleave with only datetime64[ns]
        result = timezone_frame.values
        expected = np.array(
            [
                [
                    Timestamp("2013-01-01 00:00:00"),
                    Timestamp("2013-01-02 00:00:00"),
                    Timestamp("2013-01-03 00:00:00"),
                ],
                [
                    Timestamp("2013-01-01 00:00:00-0500", tz="US/Eastern"),
                    NaT,
                    Timestamp("2013-01-03 00:00:00-0500", tz="US/Eastern"),
                ],
                [
                    Timestamp("2013-01-01 00:00:00+0100", tz="CET"),
                    NaT,
                    Timestamp("2013-01-03 00:00:00+0100", tz="CET"),
                ],
            ],
            dtype=object,
        ).T
        tm.assert_numpy_array_equal(result, expected)

    def test_values_interleave_non_unique_cols(self):
        df = DataFrame(
            [[Timestamp("20130101"), 3.5], [Timestamp("20130102"), 4.5]],
            columns=["x", "x"],
            index=[1, 2],
        )

        df_unique = df.copy()
        df_unique.columns = ["x", "y"]
        assert df_unique.values.shape == df.values.shape
        tm.assert_numpy_array_equal(df_unique.values[0], df.values[0])
        tm.assert_numpy_array_equal(df_unique.values[1], df.values[1])

    def test_values_numeric_cols(self, float_frame):
        float_frame["foo"] = "bar"

        values = float_frame[["A", "B", "C", "D"]].values
        assert values.dtype == np.float64

    def test_values_lcd(self, mixed_float_frame, mixed_int_frame):

        # mixed lcd
        values = mixed_float_frame[["A", "B", "C", "D"]].values
        assert values.dtype == np.float64

        values = mixed_float_frame[["A", "B", "C"]].values
        assert values.dtype == np.float32

        values = mixed_float_frame[["C"]].values
        assert values.dtype == np.float16

        # GH#10364
        # B uint64 forces float because there are other signed int types
        values = mixed_int_frame[["A", "B", "C", "D"]].values
        assert values.dtype == np.float64

        values = mixed_int_frame[["A", "D"]].values
        assert values.dtype == np.int64

        # B uint64 forces float because there are other signed int types
        values = mixed_int_frame[["A", "B", "C"]].values
        assert values.dtype == np.float64

        # as B and C are both unsigned, no forcing to float is needed
        values = mixed_int_frame[["B", "C"]].values
        assert values.dtype == np.uint64

        values = mixed_int_frame[["A", "C"]].values
        assert values.dtype == np.int32

        values = mixed_int_frame[["C", "D"]].values
        assert values.dtype == np.int64

        values = mixed_int_frame[["A"]].values
        assert values.dtype == np.int32

        values = mixed_int_frame[["C"]].values
        assert values.dtype == np.uint8