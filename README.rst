pycsw README
============

pycsw is an OGC CSW server implementation written in Python.

pycsw fully implements the OpenGIS Catalogue Service Implementation 
Specification [Catalogue Service for the Web]. Initial development started 
in 2010 (more formally announced in 2011). The project is certified OGC 
Compliant, and is an OGC Reference Implementation.

pycsw allows for the publishing and discovery of geospatial metadata. 
Existing repositories of geospatial metadata can also be exposed via 
OGC:CSW 2.0.2, providing a standards-based metadata and catalogue component 
of spatial data infrastructures.

pycsw is Open Source, released under an MIT license, and runs on all major 
platforms (Windows, Linux, Mac OS X).

Please read the docs at http://pycsw.org/docs for more information.

pycsw-next
==========

This is a major refactoring of pycsw, aiming at a more flexible architecture
that can help expanding pycsw's usage as well as attracting more developers.

Most of the existing codebase will be refactored or rewritten but the
underlying functional requirements of pycsw will remain or become amplified:

* Provide an open source implementation for OGC's CSW standard;
* Include interoperability features and support for various Application
  Profiles;
* Allow for flexibility and customization;
* Integrate with existing tools;
* Integrate with existing data repositories;
* Be easy to install and administer;


Architecture
------------

pycsw-next aims at becoming a general server for any OGC web service. It
features the following concepts:

* *HttpRequest* - A custom object used to standardize web requests. This is
  typically created by receiving the WSGI request from whatever web framework
  is used to expose pycsw. The default `wsgi` implementation uses werkzeug, 
  but pycsw will work just fine with flask, django or other Python web 
  frameworks as long as an `HttpRequest` object is created and fed into the
  server instead of the web framework's request;

* *Server* - The usual entrypoint for an incoming request. A server may include
  several services. The server selects the default service of each type from
  its list of services. The server also has the following responsibilities:

  * Load configuration parameters. pycsw aims at being very flexible and being
    an attractive platform for integrating with other tools (as is the case
    today with the GeoNode, CKAN, etc). Despite this, pycsw also strives to be
    easy to setup and install. This means that it must be possible to customize
    many aspects of pycsw but there should be sane defaults to all parameters.
    In addition to this, pycsw should be very easy to configure and deploy on
    different environments, such as development and production. As a result,
    the following guidelines will be honored with regard to configuration:

    * Every setting is optional and has a (secure) default value;
    * Every setting can be specified as:

      * As a parameter in a .yaml configuration file, whose path can be set as
        the `PYCSW_CONFIG` environment variable;
      * An environment variable;
      * As a keyword parameter passed when instantiating a
        ``pycsw.server.PycswServer`` object;
      * By directly manipulating the ``PycswServer`` object and its structures
        after instantiation;

  * Provide general information on points of contact and other bits of metadata
    related to the server and data provider;

* *Service* - Implementation of an OGC webservice. Initially the plan is to
  support CSW, but other other standards (WPS, SOS, ...) may be added at a
  later stage. A Service is **always** versioned. So for example, CSW version
  2.0.2 is represented as a different service from CSW version 3.0.0. Every
  service implements its own:

  * *Operations* - An OGC service has a well known set of allowed operations.
    These operate on the data and are conceptually independent of the format
    used when making the request. Likewise, the result of an operation can be
    presented back to the client in different ways. This has no impact on the
    nature of the operation. Some of the operations defined by OGC CSW 2.0.2
    are:

    * GetCapabilities
    * GetRecords
    * GetRecordById
    * DescribeRecord
    * Transaction
    * Harvest

  * *RequestParsers* - A service may be able to understand requests using
    different internet media types and different schemas. For example, a CSW
    GetCapabilities request made with KVP parameters and another with XML and 
    the OGC CSW schema are each acceptable. Each media type and schema is
    parsed differently but the underlying request leads to the same operation;

  * *ResponseRenderers* - A service may be able to return results formatted
    according to multiple output formats, for example XML with the OGC schema
    or JSON with a custom schema;

  A service may also implement additional structures, as required by the
  underlying OGC standard. CSW services also implement:

  * *Repositories* - Interfaces with the actual sources of data. Repositories
    are an abstraction over the concrete datastores. pycsw can work with many
    data sources. Support for SQLAlchemy and Django ORM will be built-in but it
    should be possible to add support for other stores easily (adding
    additional databases, filesystem based repositories, QGIS projects, etc,
    ...). Each datastore's record manipulation mechanism is encapsulated and 
    the `Repository` structure presents a uniform API to the rest of pycsw's 
    code;

  * *Records* - These represent the actual metadata that is the basic unit of
    information that is the target of a CSW server. pycsw supports multiple
    schema for data records. The default OGC csw:Record schema is supported,
    and the official application profiles' schemas (ISO, FGDC, etc) will also
    be supported. It should also be fairly easy to add custom schemas (for
    example, building a schema from a layer loaded in a QGIS project). A 
    Record must present a similar interface to both data users 
    (`RequestParser` and `ResponseRenderer`) as well as to data containers 
    (`Repository`). This means that there are two types of bindings in a 
    Record:

    * *internal bindings* - These are used to transform a record from its
      representation in each `Repository` into the common pycsw `Record`
      format. This means that every `Repository` must define a set of bindings
      to the generic `Record` structure;

    * *external bindings* - These are used to transform a `Record` from and
      into the representation used or requested by clients (csw:Record, 
      gmd:MD_Metadata, etc). This means that both `RequestParser` and
      `ResponseRenderer` objects need a mechanism for defining bindings to the
      common pycsw `Record` object;

The following is a simplified UML class diagram to put the mentioned concepts
into perspective:

.. uml::

   class HttpRequest {}
   class Server {}
   class Service {}
   class Operation {}
   class RequestParser {}
   class ResponseRenderer {}
   class Repository {}
   class Record {}

   Server - Service
   Service - Operation
   Service - RequestParser
   Service - ResponseRenderer
   Service - Csw202Service
   Csw202Service - Repository


Infrastructure
--------------

pycsw-next aims at using modern and robust tools and industry best practices.
This means:

* Having a robust testing harness with multiple steps:

  * Code linting according to PEP8;
  * Lots of unit tests;
  * Many integration tests;
  * Some functional tests;

* Adopting Continuous Deployment practices, with every commit to the master
  branch being treated as a potential release;

* Using properly isolated build environments, namely Docker containers;

* Supporting Python 3.5 and later exclusively;


Administration
--------------

pycsw-next will also feature a refactored `pycsw-admin` command line tool to
assist in performing installation and administration tasks.
It will be possible to integrate the admin functionality in other frameworks,
such as django's django-admin.

Some commands that will be available:

* pycsw-admin install pyxb [pyxb version]
* pycsw-admin csw create repository [repository options]
* pycsw-admin csw import records [import records options]
* pycsw-admin test [test options] --settings <settings file>
* pycsw-admin csw harvest [harvest options] --settings <settings file>


Concurrency
-----------

pycsw-next will use concurrent `celery` tasks where appropriate, specially in
CSW's Harvest operations


Tooling
-------

pycsw-next aims at using state-of-the-art Python tools as used in the general
industry. This includes:

* py.test - as testing framework;
* lxml - for handling XML data;
* PyXB - for working with OGC schema objects;
* celery - for asynchronous tasks;
* sphynx - for documentation;
* python standard library's logging module - for logging;
* werkzeug - for extracting HTTP parameters from the web server in the default
  wsgi application;
* gunicorn - for deploying the default wsgi application. This can be
  customized;



Installing PYXB
---------------

PyXB is used to parse and validate XML entities. While PyXB can be easily
installed with pip, the default installation does not include support for OGC
schemas. As such, it is necessary to generate the schemas after installation.
Install it with the following:

.. code:: bash

   PYXB_VERSION=1.2.4
   mkdir build && \
   cd build && \
   pip download pyxb==${PYXB_VERSION} && \
   tar -zxvf PyXB-${PYXB_VERSION}.tar.gz  && \
   cd PyXB-{PYXB_VERSION} && \
   export PYXB_ROOT=$(pwd) && \
   maintainer/genbundles @ && \
   pyxb/bundles/opengis/scripts/genbind && \
   pip install --upgrade . && \
   cd .. && \
   rm -rf build

