import ast
from typing import List


importmap = {
    "import os":"import os",
    "import string": "import strutils",
    "import datetime": "import times",
    "import urllib":"import httpclient",
    "import subprocess": "import osproc",
    "import pathlib":"",
    "import os.path":"",
    "import cmath": "import math",
    "import sqlite3":"import db_sqlite",
    "import pickle":"import json, jsonutils, marshal",
    "import webbrowser": "import browsers",
    "import asyncio":"import asyncdispatch, asyncfile, asyncnet, asyncstreams",
    "import difflib":"import diff",
    "import colorsys": "import colors",
    "import hashlib.md5": "import md5",
    "import hashlib.sha1": "import sha1",
    "import http.server": "import asynchttpserver",
    "import shlex": "import lexbase",
    "import threading": "import threadpool",
    "import urllib.parse": "import uri", 
    "import csv":"import parsecsv",
    "import argparse":"import parseopt",
    "import smtplib":"import smtp",
    "import http.cookies":"import cookies",
    "import statistics":"import stats",
    "import textwrap":"import wordwrap",
    "import winreg":"import registry",
    "import posix"	:"import posix, posix_utils",
    "import ssl":"import openssl",
    "import cgi":"import cgi",
    "import cprofile ":"import nimprof",
    "import profile ":"import nimprof",
    "import time": "import time.monotonic, monotimes",
    "import atexit":"import exitprocs",
    "import stat":"import filepermissions",
    "import os.walk":"import walkDirRec ",
    "import glob":"import walkDirRecFilter",
    "import collections.deque":"import deques",
    "import json" : "import parsejson",
    "import configparser":"import parsecfg",
    "import xml":"import parsexml, xmltree",
    "import html.parser ":"import htmlparser",
}


def get_imports(filename: str) -> List[str]:
    """
    Extract and convert import statements from a Python file.

    Parameters:
    - filename (str): The path to the Python file.

    Returns:
    - List[str]: List of converted import statements.
    """
    with open(filename, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            name = "import " + str(node.module)
            try:
                val = importmap[name]
                strings.append(val)
            except KeyError:
                continue
        elif isinstance(node, ast.Import):
            names = node.names
            for n in names:
                x = "import " + ast.unparse(n)
                try:
                    val = importmap[x]
                    strings.append(val)
                except KeyError:
                    continue
    return strings




