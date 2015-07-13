"""
Handlers for interacting with sqlalchemy's orm in order to perform database
related instructions

This module should eventually replace pycsw.core.repository
"""

import os.path
import logging

from sqlalchemy import text, func

from . import models
from .models import Record
from . import util


LOGGER = logging.getLogger(__name__)


