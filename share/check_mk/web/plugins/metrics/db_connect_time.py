#!/usr/bin/env python3

from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    metric_info,
    perfometer_info,
)

metric_info["db_connect_time"] = {
    "title": _("DB Connect Time"),
    "unit": "s",
    "color": "#03fcfc",
}

perfometer_info.append(
    {
        "type" : "logarithmic",
        "metric" : "db_connect_time",
        "half_value" : 0.1,
        "exponent" : 2,
    }
)
