# app/tasks/analyzer.py
import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any

def count_gte_by_year(df: pd.DataFrame, money_threshold: float, year_limit: int) -> int:
    # count number of films with Worldwide gross >= threshold and Year < year_limit
    c = df[(df["Worldwide gross"].notnull()) & (df["Worldwide gross"] >= money_threshold) & (df["Year"].notnull()) & (df["Year"] < year_limit)]
    return int(len(c))

def earliest_film_over(df: pd.DataFrame, money_threshold: float) -> str:
    c = df[(df["Worldwide gross"].notnull()) & (df["Worldwide gross"] > money_threshold) & (df["Year"].notnull())]
    if c.empty:
        return ""
    c = c.sort_values("Year")
    return str(c.iloc[0]["Title"])

def pearson_corr(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = ~np.isnan(a) & ~np.isnan(b)
    if mask.sum() < 2:
        return float("nan")
    return float(np.corrcoef(a[mask], b[mask])[0,1])

def linear_regression(x, y) -> Tuple[float, float]:
    """
    Returns slope, intercept (OLS)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    if mask.sum() < 2:
        return float("nan"), float("nan")
    slope, intercept, r_value, p_value, std_err = stats.linregress(x[mask], y[mask])
    return float(slope), float(intercept)
