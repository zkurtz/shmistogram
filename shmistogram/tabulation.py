"""Tabulation of series data."""

from dataclasses import dataclass
from typing import Any, Hashable, Iterable, TypeAlias

import pandas as pd

N_OBS = "n_obs"
N_VALUES = "n"
N_DISTINCT = "n_distinct"
EMPIRICAL_P = "empirical_p"

# type for an interable of hashable values:
IterableValues: TypeAlias = Iterable[Hashable]


@dataclass(kw_only=True)
class SeriesTable:
    """A table of data counts.

    Attributes:
        df: The table of counts
        n: The number of values in the input series
        n_distinct: The number of distinct values in the input series (i.e. the number of rows in `df`)
        compute_empirical_p: Whether to compute the empirical probability of each value as an extra column in `df`
    """

    df: pd.DataFrame
    n: int
    n_distinct: int
    name: str | None = None
    compute_empirical_p: bool = False

    def __post_init__(self):
        """Check the integrity of the data and to compute the empirical probability if requested."""
        isnull = pd.isnull(self.df.index)
        assert self.df[~isnull].index.is_monotonic_increasing, "Expected self.df.index to be monotonic increasing."
        assert N_OBS in self.df, "Expected self.df to have a column named 'n_obs'."
        if self.compute_empirical_p and EMPIRICAL_P not in self.df:
            self.df[EMPIRICAL_P] = self.df[N_OBS] / self.n

    def select(self, idxs: IterableValues) -> "SeriesTable":
        """Return a copy of self that includes only a subset of the distinct values.

        Args:
            idxs: The row indices of the args to include. These are named index values, not positional indices.
        """
        df = self.df.loc[idxs].copy()  # pyright: ignore
        cls = type(self)
        return cls(
            df=df,
            n=df[N_OBS].sum(),
            n_distinct=len(df),
            name=self.name,
            compute_empirical_p=self.compute_empirical_p,
        )


def tabulate(data: IterableValues, **kwargs: Any) -> SeriesTable:
    """Create series table from a data series.

    Args:
        data: The data to tabulate.
        **kwargs: Additional keyword args passed into the class constructor.
    """
    series = pd.Series(data)  # pyright: ignore
    name = getattr(data, "name", None)
    counts = series.value_counts(sort=False, dropna=False)
    df = pd.DataFrame(counts).sort_index()
    df = df.rename(columns={"count": N_OBS})
    return SeriesTable(
        df=df,
        n=len(series),
        n_distinct=len(df),
        name=str(name) if name else None,
        **kwargs,
    )
