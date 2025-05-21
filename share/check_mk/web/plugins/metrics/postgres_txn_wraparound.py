#!/usr/bin/env python3

from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    metric_info,
    perfometer_info,
)


metric_info["unfrozen_txns"] = {
    "title": _("Postgres XIDs (unfrozen)"),
    "unit": "count",
    "color": "#ff9626",
}

perfometer_info.append(
    {
        "type" : "logarithmic",
        "metric": "unfrozen_txns",
        "half_value": 700000000,
        "exponent": 2,
    }
)
