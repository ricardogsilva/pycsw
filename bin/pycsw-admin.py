#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Angelos Tzotsos <tzotsos@gmail.com>
#
# Copyright (c) 2015 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import argparse
import os
import traceback
import ConfigParser
import logging

from pycsw.core import admin
from pycsw.core.config import StaticContext

LOGGER = logging.getLogger(__name__)


class PycswAdminHandler(object):
    config = None
    config_defaults = {"table": "records",}
    context = StaticContext()

    def __init__(self):
        self.config = None

    def parse_configuration(self, config_path):
        self.config = ConfigParser.SafeConfigParser(self.config_defaults)
        self.config.readfp(open(config_path))

    def handle_db(self, args):
        database, table = self._get_db_settings()
        if args.db_command == "create":
            home = self.config.get('server', 'home')
            admin.setup_db(database, table, home)
        elif args.db_command == "optimize":
            admin.optimize_db(self.context, database, table)
        elif args.db_command == "rebuild":
            admin.rebuild_db_indexes(database, table)
        elif args.db_command == "clean":
            force = args.accept_changes
            if not force:
                msg = "This will delete all records! Continue [Y/n] "
                if raw_input(msg) == 'Y':
                    force = True
            if force:
                admin.delete_records(self.context, database, table)

    def handle_load(self, args):
        database, table = self._get_db_settings()
        admin.load_records(self.context, database, table, args.input_directory,
                           args.recursive, args.accept_changes)

    def handle_export(self, args):
        database, table = self._get_db_settings()
        admin.export_records(self.context, database, table,
                             args.output_directory)

    def handle_harvest(self, args):
        database, table = self._get_db_settings()
        url = self.config.get("server", "url")
        admin.refresh_harvested_records(self.context, database, table, url)

    def handle_sitemap(self, args):
        database, table = self._get_db_settings()
        url = self.config.get("server", "url")
        admin.gen_sitemap(self.context, database, table, url, args.output_path)

    def handle_post(self, args):
        print(admin.post_xml(args.url, args.xml, args.timeout))

    def handle_dependencies(self, args):
        print(admin.get_sysprof())

    def handle_validate(self, args):
        admin.validate_xml(args.xml, args.xml_schema)

    def get_parser(self):
        parser = argparse.ArgumentParser(
            description="PyCSW command-line configuration tool")
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Be verbose about the output")
        parser.add_argument(
            "-c", "--config", help="Filepath to pycsw configuration. "
            "Alternatively, you can set the PYCSW_CONFIG environment "
            "variable"
        )
        subparsers = parser.add_subparsers(title="Available commands")
        self._add_db_parser(subparsers)
        self._add_load_parser(subparsers)
        self._add_export_parser(subparsers)
        self._add_harvest_parser(subparsers)
        self._add_sitemap_parser(subparsers)
        self._add_post_parser(subparsers)
        self._add_dependencies_parser(subparsers)
        self._add_validate_parser(subparsers)
        return parser

    def _add_db_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "db", help="Manage repository",
            description="Perform actions on the database repository"
        )
        subsubparsers = parser.add_subparsers(title="Available commands")
        subsubs = {
            "create": ("Create a new repository", 
                       "Creates a new database repository", 
                       []),
            "optimize": ("Optimize the current repository", 
                         "Optimizes the database repository", 
                         []),
            "rebuild": ("Rebuild database indexes", 
                        "Rebuilds database indexes for the repository", 
                        []),
            "clean": ("Delete all records from the repository", 
                      "Deletes all of the metadata records from the database "
                      "repository", 
                      [
                          (("-y", "--accept-changes",), 
                           {"action": "store_true", 
                            "help": "Do not prompt for confirmation"},)
                      ],
            )
        }
        for cmd, info in subsubs.iteritems():
            help_text, description, arguments = info
            p = subsubparsers.add_parser(cmd, help=help_text, 
                                         description=description)
            for a in arguments:
                args, kwargs = a
                p.add_argument(*args, **kwargs)
            p.set_defaults(func=self.handle_db, db_command=cmd)

    def _add_load_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "load",
            help="Loads metadata records from directory into repository",
            description="Loads metadata records stored as XML files. Files "
                        "are searched in the input directory."
        )
        parser.add_argument(
            "input_directory",
            help="path to input directory to read metadata records"
        )
        parser.add_argument(
            "-r", "--recursive", help="Read sub-directories recursively",
            action="store_true")
        parser.add_argument(
            "-y", "--accept-changes", help="Force updates", action="store_true")
        parser.set_defaults(func=self.handle_load)

    def _add_export_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "export",
            help="Dump metadata records from repository into directory",
            description="Write all of the metadata records present in the "
                        "database into individual XML files. The files are "
                        "created at the specified output directory."
        )
        parser.add_argument(
            "output_directory",
            help="path to output directory to write metadata records"
        )
        parser.set_defaults(func=self.handle_export)

    def _add_harvest_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "harvest",
            help="Refresh harvested records",
            description="Refresh harvested records"
        )
        parser.set_defaults(func=self.handle_harvest)

    def _add_sitemap_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "sitemap", 
            help="Generate XML sitemap",
            description="Generate an XML sitemap file"
        )
        parser.add_argument(
            "-o", "--output-path",
            help="full path to output file. Defaults to the current directory",
            default=".")
        parser.set_defaults(func=self.handle_sitemap)

    def _add_post_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "post",
            help="Generate HTTP POST requests",
            description="Generate HTTP POST requests to an input CSW server "
                        "using an input XML file with the request"
        )
        parser.add_argument("xml", help="Path to an XML file to be POSTed")
        parser.add_argument(
            "-u", "--url", default="http://localhost:8000/",
            help="URL endpoint of the CSW server to contact. Defaults "
                 "to %(default)s"
        )
        parser.add_argument(
            "-t", "--timeout", type=int, default=30,
            help="Timeout (in seconds) for HTTP requests. Defaults "
                 "to %(default)s"
        )
        parser.set_defaults(func=self.handle_post)

    def _add_dependencies_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "dependencies",
            help="Inspect the version of installed dependencies",
            description="Inspect the version of installed dependencies"
        )
        parser.set_defaults(func=self.handle_dependencies)

    def _add_validate_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "validate",
            help="Validate XML files against schema documents",
            description="Validate an input XML file with a CSW request using "
                        "an XML schema file"
        )
        parser.add_argument("xml", help="Path to an XML file to be validated")
        parser.add_argument(
            "-x", "--xml-schema",
            help="Path to an XMl schema file to use for validation"
        )
        parser.set_defaults(func=self.handle_validate)

    def _get_db_settings(self):
        database = self.config.get("repository", "database")
        table = self.config.get('repository', 'table')
        return database, table


if __name__ == "__main__":
    handler = PycswAdminHandler()
    parser = handler.get_parser()
    args = parser.parse_args()
    log_level = logging.DEBUG if args.verbose else logging.ERROR
    logging.basicConfig(format='%(message)s', level=log_level)
    settings_path = args.config or os.environ.get("PYCSW_CONFIG")
    try:
        if settings_path is not None:
            handler.parse_configuration(settings_path)
        args.func(args)
        print("Done!")
    except Exception as err:
        LOGGER.error("Error: {}".format(err))
        traceback.print_exc()
        raise SystemExit
