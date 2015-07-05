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

import ConfigParser
import getopt
import logging
import sys

import argparse
import os

from pycsw.core import admin, config

logger = logging.getLogger(__name__)


class PycswAdminHandler(object):
    config = None
    config_defaults = {"table": "records",}
    context = config.StaticContext()

    def __init__(self):
        self.config = None

    def parse_configuration(self, config_path):
        try:
            self.config = ConfigParser.SafeConfigParser(self.config_defaults)
            self.config.readfp(settings_path)
        except AttributeError as err:
            logger.error(e)
            raise SystemExit

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
            force = args.force
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
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="Be verbose about the output")
        parser.add_argument("-s", "--settings", 
                            help="Filepath to pycsw configuration")
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
        parser = subparsers_obj.add_parser("db", help="Manage repository")
        subsubparsers = parser.add_subparsers(title="subcommands")
        subsubs = {
            "create": [],
            "optimize": [],
            "rebuild": [],
            "clean": [
                (
                    ("-y", "--accept-changes",),
                    {
                        "action": "store_true", 
                        "help": "Do not prompt for confirmation",
                    },
                )
            ],
        }
        for cmd, arguments in subsubs.iteritems():
            p = subsubparsers.add_parser(cmd)
            for a in arguments:
                args, kwargs = a
                p.add_argument(*args, **kwargs)
            p.set_defaults(func=self.handle_db, db_command=cmd)

    def _add_load_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "load", 
            help="Loads metadata records from directory into repository"
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
            help="Dump metadata records from repository into directory"
        )
        parser.add_argument(
            "output_directory", 
            help="path to output directory to write metadata records"
        )
        parser.set_defaults(func=self.handle_export)

    def _add_harvest_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "harvest", 
            help="Refresh harvested records"
        )
        parser.set_defaults(func=self.handle_harvest)

    def _add_sitemap_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "sitemap", help="Generate XML sitemap")
        parser.add_argument(
            "-o", "--output-path", 
            help="full path to output file. Defaults to the current directory",
            default=".")
        parser.set_defaults(func=self.handle_sitemap)

    def _add_post_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "post", help="Generate HTTP POST requests")
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
            "dependencies", help="Inspect the version of installed dependencies")
        parser.set_defaults(func=self.handle_dependencies)

    def _add_validate_parser(self, subparsers_obj):
        parser = subparsers_obj.add_parser(
            "validate", help="Validate XML files against schema documents")
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
    settings_path = args.settings or os.environ.get("PYCSW_SETTINGS")
    if settings_path is not None:
        handler.parse_configuration(settings_path)
    log_level = logging.DEBUG if args.verbosity >= 1 else logging.ERROR
    logging.basicConfig(format='%(message)s', level=log_level)
    args.func(args)


#def usage():
#    """Provide usage instructions"""
#    return '''
#NAME
#    pycsw-admin.py - pycsw admin utility
#
#SYNOPSIS
#    pycsw-admin.py -c <command> -f <cfg> [-h] [-p /path/to/records] [-r]
#
#    Available options:
#
#    -c    Command to be performed:
#              - setup_db
#              - load_records
#              - export_records
#              - rebuild_db_indexes
#              - optimize_db
#              - refresh_harvested_records
#              - gen_sitemap
#              - post_xml
#              - get_sysprof
#              - validate_xml
#              - delete_records
#
#    -f    Filepath to pycsw configuration
#
#    -h    Usage message
#
#    -o    path to output file
#
#    -p    path to input/output directory to read/write metadata records
#
#    -r    load records from directory recursively
#
#    -s    XML Schema
#
#    -t    Timeout (in seconds) for HTTP requests (default is 30)
#
#    -u    URL of CSW
#
#    -x    XML document
#
#    -y    force confirmation
#
#
#EXAMPLES
#
#    1.) setup_db: Creates repository tables and indexes
#
#        pycsw-admin.py -c setup_db -f default.cfg
#        
#    2.) load_records: Loads metadata records from directory into repository
#
#        pycsw-admin.py -c load_records -p /path/to/records -f default.cfg
#
#        Load records from directory recursively
#
#        pycsw-admin.py -c load_records -p /path/to/records -f default.cfg -r
#
#        Load records from directory and force updates
#
#        pycsw-admin.py -c load_records -p /path/to/records -f default.cfg -y
#
#    3.) export_records: Dump metadata records from repository into directory
#
#        pycsw-admin.py -c export_records -p /path/to/records -f default.cfg
#
#    4.) rebuild_db_indexes: Rebuild repository database indexes
#
#        pycsw-admin.py -c rebuild_db_indexes -f default.cfg
#
#    5.) optimize_db: Optimize repository database
#
#        pycsw-admin.py -c optimize_db -f default.cfg
#
#    6.) refresh_harvested_records: Refresh repository records
#        which have been harvested
#
#        pycsw-admin.py -c refresh_harvested_records -f default.cfg
#
#    7.) gen_sitemap: Generate XML Sitemap
#
#        pycsw-admin.py -c gen_sitemap -f default.cfg -o /path/to/sitemap.xml
#
#    8.) post_xml: Execute a CSW request via HTTP POST
#
#        pycsw-admin.py -c post_xml -u http://host/csw -x /path/to/request.xml
#
#    9.) get_sysprof: Get versions of dependencies
#
#        pycsw-admin.py -c get_sysprof
#
#   10.) validate_xml: Validate an XML document against an XML Schema
#
#        pycsw-admin.py -c validate_xml -x file.xml -s file.xsd
#
#   11.) delete_records: Deletes all records from repository
#
#        pycsw-admin.py -c delete_records -f default.cfg
#
#   12.) delete_records: Deletes all records from repository without prompting
#
#        pycsw-admin.py -c delete_records -f default.cfg -y
#
#'''
#
#COMMAND = None
#XML_DIRPATH = None
#CFG = None
#RECURSIVE = False
#OUTPUT_FILE = None
#CSW_URL = None
#XML = None
#XSD = None
#TIMEOUT = 30
#FORCE_CONFIRM = False
#
#if len(sys.argv) == 1:
#    print usage()
#    sys.exit(1)
#
#try:
#    OPTS, ARGS = getopt.getopt(sys.argv[1:], 'c:f:ho:p:ru:x:s:t:y')
#except getopt.GetoptError as err:
#    print '\nERROR: %s' % err
#    print usage()
#    sys.exit(2)
#
#for o, a in OPTS:
#    if o == '-c':
#        COMMAND = a
#    if o == '-f':
#        CFG = a
#    if o == '-o':
#        OUTPUT_FILE = a
#    if o == '-p':
#        XML_DIRPATH = a
#    if o == '-r':
#        RECURSIVE = True
#    if o == '-u':
#        CSW_URL = a
#    if o == '-x':
#        XML = a
#    if o == '-s':
#        XSD = a
#    if o == '-t':
#        TIMEOUT = int(a)
#    if o == '-h':  # dump help and exit
#        print usage()
#        sys.exit(3)
#    if o == '-y':
#        FORCE_CONFIRM = True
#
#if COMMAND is None:
#    print '-c <command> is a required argument'
#    sys.exit(4)
#
#if COMMAND not in ['setup_db', 'load_records', 'export_records',
#                   'rebuild_db_indexes', 'optimize_db',
#                   'refresh_harvested_records', 'gen_sitemap',
#                   'post_xml', 'get_sysprof',
#                   'validate_xml', 'delete_records']:
#    print 'ERROR: invalid command name: %s' % COMMAND
#    sys.exit(5)
#
#if CFG is None and COMMAND not in ['post_xml', 'get_sysprof', 'validate_xml']:
#    print 'ERROR: -f <cfg> is a required argument'
#    sys.exit(6)
#
#if COMMAND in ['load_records', 'export_records'] and XML_DIRPATH is None:
#    print 'ERROR: -p </path/to/records> is a required argument'
#    sys.exit(7)
#
#if COMMAND == 'gen_sitemap' and OUTPUT_FILE is None:
#    print 'ERROR: -o </path/to/sitemap.xml> is a required argument'
#    sys.exit(8)
#
#if COMMAND not in ['post_xml', 'get_sysprof', 'validate_xml']:
#    SCP = ConfigParser.SafeConfigParser()
#    SCP.readfp(open(CFG))
#
#    DATABASE = SCP.get('repository', 'database')
#    URL = SCP.get('server', 'url')
#    HOME = SCP.get('server', 'home')
#    METADATA = dict(SCP.items('metadata:main'))
#    try:
#        TABLE = SCP.get('repository', 'table')
#    except ConfigParser.NoOptionError:
#        TABLE = 'records'
#
#elif COMMAND not in ['get_sysprof', 'validate_xml']:
#    if CSW_URL is None:
#        print 'ERROR: -u <http://host/csw> is a required argument'
#        sys.exit(9)
#    if XML is None:
#        print 'ERROR: -x /path/to/request.xml is a required argument'
#        sys.exit(10)
#elif COMMAND == 'validate_xml':
#    if XML is None:
#        print 'ERROR: -x /path/to/file.xml is a required argument'
#        sys.exit(11)
#    if XSD is None:
#        print 'ERROR: -s /path/to/file.xsd is a required argument'
#        sys.exit(12)
#
#if COMMAND == 'setup_db':
#    try:
#        admin.setup_db(DATABASE, TABLE, HOME)
#    except Exception as err:
#        print err
#        print 'ERROR: DB creation error.  Database tables already exist'
#        print 'Delete tables or database to reinitialize'
#elif COMMAND == 'load_records':
#    admin.load_records(CONTEXT, DATABASE, TABLE, XML_DIRPATH, RECURSIVE, FORCE_CONFIRM)
#elif COMMAND == 'export_records':
#    admin.export_records(CONTEXT, DATABASE, TABLE, XML_DIRPATH)
#elif COMMAND == 'rebuild_db_indexes':
#    admin.rebuild_db_indexes(DATABASE, TABLE)
#elif COMMAND == 'optimize_db':
#    admin.optimize_db(CONTEXT, DATABASE, TABLE)
#elif COMMAND == 'refresh_harvested_records':
#    admin.refresh_harvested_records(CONTEXT, DATABASE, TABLE, URL)
#elif COMMAND == 'gen_sitemap':
#    admin.gen_sitemap(CONTEXT, DATABASE, TABLE, URL, OUTPUT_FILE)
#elif COMMAND == 'post_xml':
#    print admin.post_xml(CSW_URL, XML, TIMEOUT)
#elif COMMAND == 'get_sysprof':
#    print admin.get_sysprof()
#elif COMMAND == 'validate_xml':
#    admin.validate_xml(XML, XSD)
#elif COMMAND == 'delete_records':
#    if not FORCE_CONFIRM:
#        if raw_input('This will delete all records! Continue? [Y/n] ') == 'Y':
#            FORCE_CONFIRM = True
#    if FORCE_CONFIRM:
#        admin.delete_records(CONTEXT, DATABASE, TABLE)
#
#print 'Done'
