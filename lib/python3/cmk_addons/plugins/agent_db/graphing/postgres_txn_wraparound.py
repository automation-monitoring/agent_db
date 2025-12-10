#!/usr/bin/env python3


from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Metric,
    Unit,
    Color,
    StrictPrecision,
    DecimalNotation
)
from cmk.graphing.v1.perfometers import Perfometer, FocusRange, Open, Closed


metric_unfrozen_txns = Metric(
    name="unfrozen_txns",
    title=Title("Postgres XIDs (unfrozen)"),
    unit=Unit(DecimalNotation(""), StrictPrecision(0)),
    color=Color.LIGHT_ORANGE,
)


perfometer_unfrozen_txns = Perfometer(
    name="unfrozen_txns",
    segments=["unfrozen_txns"],
    focus_range=FocusRange(Closed(0), Open(2000000000)),
)
