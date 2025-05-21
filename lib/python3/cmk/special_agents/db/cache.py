#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# SPDX-FileCopyrightText: © PL Automation Monitoring GmbH <pl@automation-monitoring.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of the checkmk "Database Special Agent" agent_db (https://github.com/automation-monitoring/agent_db)

import os
import hashlib
import pickle
import time


def generate_cache_key(db_host, db_cstr, statement):
    """
    Generates a unique cache key for storing SQL query results.

    Parameters:
    - db_cstr (str): Database connection string, used to differentiate caches across different databases.
    - statement (str): The SQL statement for which the cache key is being generated.

    Returns:
    - str: A SHA256 hash digest of the database connection string and SQL statement, serving as a unique cache key.
    """
    # sqlstatement = hashlib.sha256((sqlstatement).encode()).hexdigest()
    if db_cstr.startswith("("):
        db_cstr = f"dsn_{hashlib.sha256(db_cstr.encode()).hexdigest()}"
    cache_key = f"{db_host}_{db_cstr}_{statement}"
    return cache_key


def get_cache(cache_key, cache_dir, max_cache_age_sec):
    """
    Checks if there is a valid cache entry for the given cache key and that it is within the specified age limit.

    Parameters:
    - cache_key (str): The cache key to look up in the cache directory.
    - max_age_seconds (int): The maximum age in seconds for the cache to be considered valid.

    Returns:
    - tuple: A tuple containing the modification time of the cache file and the cached data if a valid cache is found and is within the age limit.
    - None: If the cache does not exist or is older than the specified maximum age.
    """

    cache_file = os.path.join(cache_dir, cache_key + ".pkl")

    if os.path.exists(cache_file):
        mtime_cache_file = int(os.path.getmtime(cache_file))
        cache_age = time.time() - mtime_cache_file
        if cache_age < max_cache_age_sec:
            with open(cache_file, "rb") as f:
                return (mtime_cache_file, pickle.load(f))
    return None


def write_cache(cache_dir, cache_key, data):
    """
    Writes the provided data to a cache file identified by the cache key.

    Parameters:
    - cache_key (str): The cache key under which the data should be stored.
    - data: The data to be cached. This can be any object that can be serialized by pickle.

    Returns:
    - None
    """
    cache_file = os.path.join(cache_dir, cache_key + ".pkl")
    with open(cache_file, "wb") as f:
        pickle.dump(data, f)


def get_cache_time_in_seconds(state_statement_cfg):
    """
    Convert cache time from minutes to seconds.

    Args:
        state_statement_cfg (dict): Configuration of the current statement.

    Returns:
        int or None: Cache time in seconds, or None if not specified.
    """
    cache_time_min = state_statement_cfg.get("cache_time_min")
    return cache_time_min * 60 if cache_time_min is not None else None
