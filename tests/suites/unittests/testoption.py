from nose.tools import eq_


class TestPycswOption(object):

    @classmethod
    def setup_class(cls):
        cls.option_name = "foo"
        cls.option_default = "bar"
        cls.option_section = "baz"
        cls.option_config_parser_name = "foooo"
        cls.option = cls(name=cls.option_name,
                         default=cls.option_default,
                         section=cls.option_section,
                         config_parser_name=cls.option_config_parser_name)
