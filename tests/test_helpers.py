# -*- coding: utf-8 -*-

import types

from mock import sentinel, MagicMock

from sceptre.stack_group import StackGroup
from sceptre.helpers import camel_to_snake_case
from sceptre.helpers import recurse_into_sub_stack_groups
from sceptre.helpers import get_name_tuple
from sceptre.helpers import resolve_stack_name
from sceptre.helpers import get_external_stack_name


class TestHelpers(object):

    def test_camel_to_snake_case(self):
        snake_case_string = camel_to_snake_case("Cmd")
        assert snake_case_string == "cmd"
        snake_case_string = camel_to_snake_case("ASGScalingProcesses")
        assert snake_case_string == "asg_scaling_processes"

    def test_recurse_into_sub_stack_groups(self):
        stack_group = MagicMock(spec=StackGroup)
        stack_group.name = "stack_group"
        stack_group.sub_stack_groups = []

        def do(self):
            return {self.name: sentinel.response}

        stack_group.do = types.MethodType(
            recurse_into_sub_stack_groups(do),
            stack_group
        )

        response = stack_group.do()
        assert response == {"stack_group": sentinel.response}

    def test_recurse_into_sub_stack_groups_with_non_leaf_object(self):
        class MockStackGroup(object):

            def __init__(self, name):
                self.name = name
                self.sub_stack_groups = []

            @recurse_into_sub_stack_groups
            def do(self):
                return {self.name: sentinel.response}

        mock_group = MockStackGroup("stack_group_1")

        # Add leaf sub-stack_groups
        mock_group.sub_stack_groups = [
            MockStackGroup("stack_group_2"), MockStackGroup("stack_group_3")
        ]

        response = mock_group.do()
        assert response == {
            "stack_group_1": sentinel.response,
            "stack_group_2": sentinel.response,
            "stack_group_3": sentinel.response
        }

    def test_get_name_tuple(self):
        result = get_name_tuple("dev/ew1/jump-host")
        assert result == ("dev", "ew1", "jump-host")

    def test_resolve_stack_name(self):
        result = resolve_stack_name("dev/ew1/subnet", "vpc")
        assert result == "dev/ew1/vpc"
        result = resolve_stack_name("dev/ew1/subnet", "prod/ue1/vpc")
        assert result == "prod/ue1/vpc"

    def test_get_external_stack_name(self):
        result = get_external_stack_name("prj", "dev/ew1/jump-host")
        assert result == "prj-dev-ew1-jump-host"
