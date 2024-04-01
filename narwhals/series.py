from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from narwhals.dtypes import to_narwhals_dtype
from narwhals.translate import get_pandas
from narwhals.translate import get_polars

if TYPE_CHECKING:
    from typing_extensions import Self


class Series:
    def __init__(
        self,
        series: Any,
        *,
        is_polars: bool = False,
    ) -> None:
        from narwhals._pandas_like.series import PandasSeries

        self._is_polars = is_polars
        if hasattr(series, "__narwhals_series__"):
            self._series = series.__narwhals_series__()
            return
        if is_polars or (
            (pl := get_polars()) is not None and isinstance(series, pl.Series)
        ):
            self._series = series
            self._is_polars = True
            return
        if (pd := get_pandas()) is not None and isinstance(series, pd.Series):
            self._series = PandasSeries(series, implementation="pandas")
            return
        msg = f"Expected pandas or Polars Series, got: {type(series)}"  # pragma: no cover
        raise TypeError(msg)  # pragma: no cover

    def _extract_native(self, arg: Any) -> Any:
        from narwhals.expression import Expr

        if not self._is_polars:
            return arg
        if isinstance(arg, Series):
            return arg._series
        if isinstance(arg, Expr):
            import polars as pl

            return arg._call(pl)
        return arg

    def _from_series(self, series: Any) -> Self:
        return self.__class__(series, is_polars=self._is_polars)

    def __repr__(self) -> str:  # pragma: no cover
        header = " Narwhals Series                                 "
        length = len(header)
        return (
            "┌"
            + "─" * length
            + "┐\n"
            + f"|{header}|\n"
            + "| Use `narwhals.to_native()` to see native output |\n"
            + "└"
            + "─" * length
            + "┘"
        )

    def alias(self, name: str) -> Self:
        return self._from_series(self._series.alias(name))

    def __len__(self) -> int:
        return len(self._series)

    @property
    def name(self) -> str:
        return self._series.name  # type: ignore[no-any-return]

    @property
    def dtype(self) -> Any:
        return to_narwhals_dtype(self._series.dtype, is_polars=self._is_polars)

    @property
    def shape(self) -> tuple[int]:
        return self._series.shape  # type: ignore[no-any-return]

    def rename(self, name: str) -> Self:
        return self._from_series(self._series.rename(name))

    def cast(
        self,
        dtype: Any,
    ) -> Self:
        return self._from_series(self._series.cast(dtype))

    def item(self) -> Any:
        return self._series.item()

    def is_between(
        self, lower_bound: Any, upper_bound: Any, closed: str = "both"
    ) -> Self:
        return self._from_series(
            self._series.is_between(lower_bound, upper_bound, closed)
        )

    def is_in(self, other: Any) -> Self:
        return self._from_series(self._series.is_in(self._extract_native(other)))

    def is_null(self) -> Self:
        return self._from_series(self._series.is_null())

    def drop_nulls(self) -> Self:
        return self._from_series(self._series.drop_nulls())

    def n_unique(self) -> int:
        return self._series.n_unique()  # type: ignore[no-any-return]

    def unique(self) -> Self:
        return self._from_series(self._series.unique())

    def zip_with(self, mask: Self, other: Self) -> Self:
        return self._from_series(
            self._series.zip_with(self._extract_native(mask), self._extract_native(other))
        )

    def sample(
        self,
        n: int | None = None,
        fraction: float | None = None,
        *,
        with_replacement: bool = False,
    ) -> Self:
        return self._from_series(
            self._series.sample(n=n, fraction=fraction, with_replacement=with_replacement)
        )

    def to_numpy(self) -> Any:
        return self._series.to_numpy()

    def to_pandas(self) -> Any:
        return self._series.to_pandas()

    def mean(self) -> Any:
        return self._series.mean()

    def std(self) -> Any:
        return self._series.std()

    def __gt__(self, other: Any) -> Series:
        return self._series.__gt__(self._extract_native(other))  # type: ignore[no-any-return]

    def __lt__(self, other: Any) -> Series:
        return self._series.__lt__(self._extract_native(other))  # type: ignore[no-any-return]
