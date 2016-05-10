"""Integration tests for the CSW 2.0.2 service"""

import pytest
from pyxb.utils import domutils
from pyxb.bundles.opengis import csw_2_0_2
from pyxb.bundles.opengis import filter as fes
from pyxb.bundles.opengis import gml

domutils.BindingDOMSupport.DeclareNamespace(csw_2_0_2.Namespace, "csw")


@pytest.mark.integration
class TestGetRecords:

    def test_get_records(self):
        # the current code is merely an example of how to construct a
        # GetRecords request with pyxb
        request = csw_2_0_2.GetRecords(
            service="CSW",
            version="2.0.2",
            startPosition=1,
            maxRecords=10,
            outputFormat="application/xml",
            outputSchema="http://www.isotc211.org/2005/gmd",
            resultType="results",
            AbstractQuery=csw_2_0_2.Query(
                typeNames=[csw_2_0_2.Namespace.createExpandedName("Record")],
                ElementSetName="full",
                Constraint=csw_2_0_2.Constraint(
                    version="1.1.0",
                    Filter=fes.Filter(
                        fes.Or(
                            fes.And(
                                fes.PropertyIsLessThanOrEqualTo(
                                    fes.PropertyName("apiso:TempExtent_end"),
                                    fes.Literal("2020-12-31T23:59:59.000")
                                ),
                                fes.PropertyIsGreaterThanOrEqualTo(
                                    fes.PropertyName("apiso:TempExtent_begin"),
                                    fes.Literal("2009-08-10T00:00:00.000")
                                ),
                                fes.PropertyIsEqualTo(
                                    fes.PropertyName("apiso:ParentIdentifier"),
                                    fes.Literal("some:identifier")
                                ),
                                fes.BBOX(
                                    fes.PropertyName("apiso:BoundingBox"),
                                    gml.Envelope(
                                        lowerCorner="-170.169492 -54.067797",
                                        upperCorner="163.050847 89.322034"
                                    )
                                )
                            ),
                            fes.And(
                                fes.PropertyIsLessThanOrEqualTo(
                                    fes.PropertyName("apiso:TempExtent_end"),
                                    fes.Literal("2020-12-31T23:59:59.000")
                                ),
                                fes.PropertyIsGreaterThanOrEqualTo(
                                    fes.PropertyName("apiso:TempExtent_begin"),
                                    fes.Literal("2009-08-10T00:00:00.000")
                                ),
                                fes.PropertyIsEqualTo(
                                    fes.PropertyName("apiso:ParentIdentifier"),
                                    fes.Literal("another:identifier")
                                ),
                                fes.BBOX(
                                    fes.PropertyName("apiso:BoundingBox"),
                                    gml.Envelope(
                                        lowerCorner="-170.169492 -54.067797",
                                        upperCorner="163.050847 89.322034"
                                    )
                                )
                            )
                        )
                    )
                ),
                SortBy=fes.SortBy(
                    fes.SortPropertyType(
                        PropertyName="apiso:TempExtent_end",
                        SortOrder="DESC"
                    )
                )
            )
        )
        rendered_request = request.toDOM().toprettyxml()
