# -*- coding: utf-8 -*-
# cython: language_level=3
# BSD 3-Clause License
#
# Copyright (c) 2020-2022, Faster Speeding
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# pyright: reportIncompatibleMethodOverride=none
# pyright: reportUnknownMemberType=none
# pyright: reportPrivateUsage=none
# This leads to too many false-positives around mocks.

import asyncio
import contextlib
import inspect
import types
from unittest import mock

import hikari
import pytest

import tanjun

mock_global_loader_1 = mock.Mock(tanjun.components.AbstractComponentLoader)
mock_global_loader_2 = mock.Mock(tanjun.components.AbstractComponentLoader)
mock_global_loader_3 = mock.Mock(tanjun.components.AbstractComponentLoader)


class TestComponent:
    def test_loop_property(self):
        mock_loop = mock.Mock()
        component = tanjun.Component()
        component._loop = mock_loop

        assert component.loop is mock_loop

    def test_name_property(self):
        assert tanjun.Component(name="aye").name == "aye"

    def test_metadata_property(self):
        component = tanjun.Component()

        assert component.metadata == {}

        component.metadata["foo"] = "bar"

        assert component.metadata == {"foo": "bar"}

    def test_defaults_to_ephemeral_property(self):
        assert tanjun.Component().defaults_to_ephemeral is None

    @pytest.mark.skip(reason="TODO")
    def test_copy(self):
        ...

    def test_load_from_scope(self):
        # Some of the variables in this test have a type: ignore and noqa on them,
        # this is to silence warnings about these variables being "unused" which
        # we ignore in this case as we're testing that detect_command can deal with
        # ignoring variable noise.
        baz = 1  # type: ignore  # noqa: F841
        mock_loader_1 = mock.Mock(tanjun.components.AbstractComponentLoader)
        foo = None  # type: ignore  # noqa: F841
        bar = object()  # type: ignore  # noqa: F841
        mock_loader_2 = mock.Mock(tanjun.components.AbstractComponentLoader)
        mock_loader_3 = mock.Mock(tanjun.components.AbstractComponentLoader)

        component = tanjun.Component()

        result = component.load_from_scope()

        assert result is component
        mock_loader_1.load_into_component.assert_called_once_with(component)
        mock_loader_2.load_into_component.assert_called_once_with(component)
        mock_loader_3.load_into_component.assert_called_once_with(component)

    def test_load_from_scope_when_including_globals(self):
        # Some of the variables in this test have a type: ignore and noqa on them,
        # this is to silence warnings about these variables being "unused" which
        # we ignore in this case as we're testing that detect_command can deal with
        # ignoring variable noise.
        baz = 1  # type: ignore  # noqa: F841
        mock_loader_1 = mock.Mock(tanjun.components.AbstractComponentLoader)
        foo = None  # type: ignore  # noqa: F841
        mock_loader_2 = mock.Mock(tanjun.components.AbstractComponentLoader)
        mock_owned_slash_command = mock.Mock(tanjun.abc.SlashCommand)  # type: ignore  # noqa: F841
        mock_loader_3 = mock.Mock(tanjun.components.AbstractComponentLoader)
        bar = object()  # type: ignore  # noqa: F841

        component = tanjun.Component()

        result = component.load_from_scope(include_globals=True)

        assert result is component
        mock_loader_1.load_into_component.assert_called_once_with(component)
        mock_loader_2.load_into_component.assert_called_once_with(component)
        mock_loader_3.load_into_component.assert_called_once_with(component)
        mock_global_loader_1.load_into_component.assert_called_once_with(component)
        mock_global_loader_2.load_into_component.assert_called_once_with(component)
        mock_global_loader_3.load_into_component.assert_called_once_with(component)
        mock_global_loader_1.reset_mock()
        mock_global_loader_2.reset_mock()
        mock_global_loader_3.reset_mock()

    def test_load_from_scope_with_explicitly_passed_scope(self):
        mock_un_used_loader = mock.Mock(tanjun.components.AbstractComponentLoader)
        mock_loader_1 = mock.Mock(tanjun.components.AbstractComponentLoader)
        mock_loader_2 = mock.Mock(tanjun.components.AbstractComponentLoader)
        mock_loader_3 = mock.Mock(tanjun.components.AbstractComponentLoader)
        scope = {
            "foo": "bar",
            "a_command": mock_loader_1,
            "bar": None,
            "other_command": mock_loader_2,
            "buz": object(),
            "a": mock_loader_3,
            "owned_slash_command": mock.Mock(tanjun.abc.SlashCommand),
            "owned_message_command": mock.Mock(tanjun.abc.MessageCommand),
        }

        component = tanjun.Component()

        result = component.load_from_scope(scope=scope)

        assert result is component
        mock_un_used_loader.load_into_component.assert_not_called()
        mock_loader_1.load_into_component.assert_called_once_with(component)
        mock_loader_2.load_into_component.assert_called_once_with(component)
        mock_loader_3.load_into_component.assert_called_once_with(component)

    def test_load_from_scope_when_both_include_globals_and_passed_scope(self):
        component = tanjun.Component()
        with pytest.raises(ValueError, match="Cannot specify include_globals as True when scope is passed"):
            component.load_from_scope(include_globals=True, scope={})  # type: ignore

    def test_load_from_scope_when_stack_inspection_not_supported(self):
        component = tanjun.Component()

        with mock.patch.object(inspect, "currentframe", return_value=None):
            with pytest.raises(
                RuntimeError,
                match="Stackframe introspection is not supported in this runtime. Please explicitly pass `scope`.",
            ):
                component.load_from_scope()

    def test_set_ephemeral_default(self):
        client = tanjun.Component().set_ephemeral_default(False)

        assert client.defaults_to_ephemeral is False

    def test_set_metadata(self):
        component = tanjun.Component()
        key = mock.Mock()
        value = mock.Mock()

        result = component.set_metadata(key, value)

        assert result is component
        assert component.metadata[key] is value

    def test_set_slash_hooks(self):
        mock_hooks = mock.Mock()
        component = tanjun.Component()

        result = component.set_slash_hooks(mock_hooks)

        assert result is component
        assert component.slash_hooks is mock_hooks

    def test_set_slash_hooks_when_None(self):
        component = tanjun.Component().set_slash_hooks(mock.Mock())

        result = component.set_slash_hooks(None)

        assert result is component
        assert component.slash_hooks is None

    def test_set_message_hooks(self):
        mock_hooks = mock.Mock()
        component = tanjun.Component()

        result = component.set_message_hooks(mock_hooks)

        assert result is component
        assert component.message_hooks is mock_hooks

    def test_set_message_hooks_when_None(self):
        component = tanjun.Component().set_message_hooks(mock.Mock())

        result = component.set_message_hooks(None)

        assert result is component
        assert component.message_hooks is None

    def test_set_hooks(self):
        mock_hooks = mock.Mock()
        component = tanjun.Component()

        result = component.set_hooks(mock_hooks)

        assert result is component
        assert component.hooks is mock_hooks

    def test_set_hooks_when_None(self):
        component = tanjun.Component().set_hooks(mock.Mock())

        result = component.set_hooks(None)

        assert result is component
        assert component.hooks is None

    def test_add_check(self):
        mock_check = mock.Mock()
        component = tanjun.Component()

        result = component.add_check(mock_check)

        assert result is component

    def test_add_check_when_already_present(self):
        mock_check = mock.Mock()
        component = tanjun.Component().add_check(mock_check)

        with mock.patch.object(tanjun.checks, "InjectableCheck") as InjectableCheck:
            result = component.add_check(mock_check)

            InjectableCheck.assert_not_called()

        assert list(component.checks).count(mock_check) == 1
        assert result is component

    def test_remove_check(self):
        component = tanjun.Component().add_check(mock.Mock())

        result = component.remove_check(next(iter(component.checks)))

        assert result is component
        assert not component.checks

    def test_remove_check_when_not_present(self):
        with pytest.raises(ValueError, match=".+"):
            tanjun.Component().remove_check(mock.Mock())

    def test_with_check(self):
        add_check = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_check": add_check}),
        )()
        mock_check = mock.Mock()

        result = component.with_check(mock_check)

        assert result is mock_check
        add_check.assert_called_once_with(mock_check)

    def test_add_client_callback(self):
        mock_callback = mock.Mock()
        mock_other_callback = mock.Mock()
        component = tanjun.Component()

        result = component.add_client_callback("aye", mock_callback).add_client_callback("aye", mock_other_callback)

        assert result is component
        assert component.get_client_callbacks("aye") == [mock_callback, mock_other_callback]

    def test_add_client_callback_when_already_present(self):
        mock_callback = mock.Mock()
        component = tanjun.Component().add_client_callback("baaa", mock_callback)

        result = component.add_client_callback("baaa", mock_callback)

        assert result is component
        assert list(component.get_client_callbacks("baaa")).count(mock_callback) == 1

    def test_add_client_callback_when_client_bound(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client)

        result = component.add_client_callback("aye", mock_callback)

        assert result is component
        assert component.get_client_callbacks("aye") == [mock_callback]
        mock_client.add_client_callback.assert_called_once_with("aye", mock_callback)

    def test_remove_client_callback(self):
        mock_callback = mock.Mock()
        mock_other_callback = mock.Mock()
        component = (
            tanjun.Component()
            .add_client_callback("baye", mock_callback)
            .add_client_callback("baye", mock_other_callback)
        )

        component.remove_client_callback("baye", mock_callback)

        assert component.get_client_callbacks("baye") == [mock_other_callback]

    def test_remove_client_callback_when_name_not_found(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()

        with pytest.raises(KeyError):
            tanjun.Component().bind_client(mock_client).remove_client_callback("bay", mock_callback)

        mock_client.remove_client_callback.assert_not_called()

    def test_remove_client_callback_when_callback_not_found(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        mock_other_callback = mock.Mock()
        component = tanjun.Component().bind_client(mock_client).add_client_callback("sex", mock_other_callback)

        with pytest.raises(ValueError, match=".+"):
            component.remove_client_callback("sex", mock_callback)

        mock_client.remove_client_callback.assert_not_called()
        assert component.get_client_callbacks("sex") == [mock_other_callback]

    def test_remove_client_callback_when_client_bound(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().add_client_callback("bay", mock_callback).bind_client(mock_client)

        component.remove_client_callback("bay", mock_callback)

        assert component.get_client_callbacks("bay") == ()
        mock_client.remove_client_callback.assert_called_once_with("bay", mock_callback)

    def test_remove_client_callback_when_no_callbacks_left(self):
        mock_callback = mock.Mock()
        component = tanjun.Component().add_client_callback("slay", mock_callback)

        component.remove_client_callback("slay", mock_callback)

        assert component.get_client_callbacks("slay") == ()

    def test_with_client_callback(self):
        add_client_callback = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_client_callback": add_client_callback}),
        )()
        mock_callback = mock.Mock()

        result = component.with_client_callback("aye")(mock_callback)

        assert result is mock_callback
        add_client_callback.assert_called_once_with("aye", mock_callback)

    def test_add_command_for_message_command(self):
        mock_command = mock.Mock(tanjun.abc.MessageCommand)
        add_slash_command = mock.Mock()
        add_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"add_message_command": add_message_command, "add_slash_command": add_slash_command}
            ),
        )()

        result = component.add_command(mock_command)

        assert result is component
        add_message_command.assert_called_once_with(mock_command)
        add_slash_command.assert_not_called()

    def test_add_command_for_slash_command(self):
        mock_command = mock.Mock(tanjun.abc.SlashCommand)
        add_slash_command = mock.Mock()
        add_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"add_message_command": add_message_command, "add_slash_command": add_slash_command}
            ),
        )()

        result = component.add_command(mock_command)

        assert result is component
        add_slash_command.assert_called_once_with(mock_command)
        add_message_command.assert_not_called()

    def test_add_command_for_unknown_type(self):
        mock_command = mock.Mock()
        add_slash_command = mock.Mock()
        add_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"add_message_command": add_message_command, "add_slash_command": add_slash_command}
            ),
        )()

        with pytest.raises(
            ValueError,
            match=f"Unexpected object passed, expected a MessageCommand or BaseSlashCommand but got {type(mock_command)}",
        ):
            component.add_command(mock_command)

        add_slash_command.assert_not_called()
        add_message_command.assert_not_called()

    def test_remove_command_for_message_command(self):
        mock_command = mock.Mock(tanjun.abc.MessageCommand)
        remove_message_command = mock.Mock()
        remove_slash_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"remove_message_command": remove_message_command, "remove_slash_command": remove_slash_command}
            ),
        )()

        result = component.remove_command(mock_command)

        assert result is component
        remove_message_command.assert_called_once_with(mock_command)
        remove_slash_command.assert_not_called()

    def test_remove_command_for_slash_command(self):
        mock_command = mock.Mock(tanjun.abc.SlashCommand)
        remove_slash_command = mock.Mock()
        remove_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"remove_message_command": remove_message_command, "remove_slash_command": remove_slash_command}
            ),
        )()

        component.remove_command(mock_command)

        remove_slash_command.assert_called_once_with(mock_command)
        remove_message_command.assert_not_called()

    def test_remove_command_for_unknown_type(self):
        mock_command = mock.Mock()
        remove_slash_command = mock.Mock()
        remove_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update(
                {"remove_message_command": remove_message_command, "remove_slash_command": remove_slash_command}
            ),
        )()

        with pytest.raises(
            ValueError,
            match=f"Unexpected object passed, expected a MessageCommand or BaseSlashCommand but got {type(mock_command)}",
        ):
            component.remove_command(mock_command)

        remove_slash_command.assert_not_called()
        remove_message_command.assert_not_called()

    def test_with_command(self):
        add_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent", (tanjun.Component,), exec_body=lambda ns: ns.update({"add_command": add_command})
        )()
        mock_command = mock.Mock()

        result = component.with_command(mock_command)

        assert result is mock_command
        add_command.assert_called_once_with(mock_command)
        mock_command.copy.assert_not_called()

    def test_with_command_when_copy(self):
        add_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent", (tanjun.Component,), exec_body=lambda ns: ns.update({"add_command": add_command})
        )()
        mock_command = mock.Mock()

        result = component.with_command(copy=True)(mock_command)

        assert result is mock_command.copy.return_value
        add_command.assert_called_once_with(mock_command.copy.return_value)
        mock_command.copy.assert_called_once_with()

    def test_add_slash_command(self):
        mock_command = mock.Mock()
        mock_command.name = "gay"
        component = tanjun.Component()

        result = component.add_slash_command(mock_command)

        assert result is component
        assert mock_command in component.slash_commands
        mock_command.bind_component.assert_called_once_with(component)
        mock_command.bind_client.assert_not_called()

    def test_add_slash_command_when_already_present(self):
        mock_command = mock.Mock()
        mock_command.name = "gay"
        component = tanjun.Component().add_slash_command(mock_command)
        mock_command.reset_mock()

        result = component.add_slash_command(mock_command)

        assert result is component
        assert list(component.slash_commands).count(mock_command) == 1
        mock_command.bind_component.assert_not_called()
        mock_command.bind_client.assert_not_called()

    def test_add_slash_command_when_bound_to_a_client(self):
        mock_command = mock.Mock()
        mock_command.name = "gay"
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client)

        result = component.add_slash_command(mock_command)

        assert result is component
        assert mock_command in component.slash_commands
        mock_command.bind_component.assert_called_once_with(component)
        mock_command.bind_client.assert_called_once_with(mock_client)

    def test_remove_slash_command(self):
        mock_command = mock.Mock()
        mock_command.name = "42231"
        component = tanjun.Component().add_slash_command(mock_command)

        result = component.remove_slash_command(mock_command)

        assert result is component
        assert not component.slash_commands

    def test_remove_slash_command_when_not_found(self):
        mock_command = mock.Mock()
        mock_command.name = "42231"

        with pytest.raises(ValueError, match=".+"):
            tanjun.Component().remove_slash_command(mock_command)

    def test_with_slash_command(self):
        mock_command = mock.Mock()
        add_slash_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_slash_command": add_slash_command}),
        )()

        result = component.with_slash_command(mock_command)

        assert result is mock_command
        add_slash_command.assert_called_once_with(mock_command)
        mock_command.copy.assert_not_called()

    def test_with_slash_command_when_copy(self):
        mock_command = mock.Mock()
        add_slash_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_slash_command": add_slash_command}),
        )()

        result = component.with_slash_command(copy=True)(mock_command)

        assert result is mock_command.copy.return_value
        add_slash_command.assert_called_once_with(mock_command.copy.return_value)
        mock_command.copy.assert_called_once_with()

    def test_add_message_command(self):
        component = tanjun.Component(strict=True)
        mock_command = mock.Mock(names=("a", "b"))

        result = component.add_message_command(mock_command)

        assert result is component
        assert mock_command in component.message_commands
        mock_command.bind_client.assert_not_called()
        mock_command.bind_component.assert_called_once_with(component)

    def test_add_message_command_when_already_registered(self):
        mock_command = mock.Mock(names=("a", "b"))
        component = tanjun.Component(strict=True).add_message_command(mock_command)
        mock_command.reset_mock()

        result = component.add_message_command(mock_command)

        assert result is component
        mock_command.bind_client.assert_not_called()
        mock_command.bind_component.assert_not_called()
        assert list(component.message_commands).count(mock_command) == 1

    def test_add_message_command_when_already_client_bound(self):
        mock_client = mock.Mock()
        component = tanjun.Component(strict=True).bind_client(mock_client)
        mock_command = mock.Mock(names=("a", "b"))

        result = component.add_message_command(mock_command)

        assert result is component
        assert mock_command in component.message_commands
        mock_command.bind_client.assert_called_once_with(mock_client)
        mock_command.bind_component.assert_called_once_with(component)

    def test_add_message_command_when_strict(self):
        mock_client = mock.Mock()
        component = tanjun.Component(strict=True).bind_client(mock_client)
        mock_command = mock.Mock(names=("a", "b", "f"))

        result = component.add_message_command(mock_command)

        assert result is component
        mock_command.bind_client.assert_called_once_with(mock_client)
        mock_command.bind_component.assert_called_once_with(component)
        assert mock_command in component.message_commands
        assert component._names_to_commands == {"a": mock_command, "b": mock_command, "f": mock_command}

    def test_add_message_command_when_strict_and_space_in_a_name(self):
        component = tanjun.Component(strict=True)
        mock_command = mock.Mock(names=("a b",))

        with pytest.raises(ValueError, match="Command name cannot contain spaces for this component implementation"):
            component.add_message_command(mock_command)

        mock_command.bind_client.assert_not_called()
        mock_command.bind_component.assert_not_called()

    def test_add_message_command_when_strict_and_conflict_found(self):
        component = tanjun.Component(strict=True).add_message_command(mock.Mock(names=("a", "bb")))
        mock_command = mock.Mock(names=("a", "bb", "cccc", "dd"))

        with pytest.raises(
            ValueError,
            match=(
                "Sub-command names must be unique in a strict component. "
                "The following conflicts were found (?:a, bb)|(?:bb, a)"
            ),
        ):
            component.add_message_command(mock_command)

        mock_command.bind_client.assert_not_called()
        mock_command.bind_component.assert_not_called()

    def test_remove_message_command(self):
        mock_command = mock.Mock()
        mock_command.name = "a"
        component = tanjun.Component().add_message_command(mock_command)

        result = component.remove_message_command(mock_command)

        assert result is component
        assert not component.message_commands

    def test_remove_message_command_when_not_found(self):
        mock_command = mock.Mock()
        mock_command.name = "a"

        with pytest.raises(ValueError, match=".+"):
            tanjun.Component().remove_message_command(mock_command)

    def test_remove_message_command_when_strict(self):
        mock_command = mock.Mock(names=("a", "b", "f"))
        mock_other_command = mock.Mock(names=("abba", "babba"))
        component = (
            tanjun.Component(strict=True).add_message_command(mock_other_command).add_message_command(mock_command)
        )

        component.remove_message_command(mock_command)

        assert mock_command not in component.message_commands
        assert component._names_to_commands == {"abba": mock_other_command, "babba": mock_other_command}

    def test_with_message_command(self):
        mock_command = mock.Mock()
        add_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_message_command": add_message_command}),
        )()

        result = component.with_message_command(mock_command)

        assert result is mock_command
        add_message_command.assert_called_once_with(mock_command)

    def test_with_message_command_when_copy(self):
        mock_command = mock.Mock()
        add_message_command = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_message_command": add_message_command}),
        )()

        result = component.with_message_command(copy=True)(mock_command)

        assert result is mock_command.copy.return_value
        add_message_command.assert_called_once_with(mock_command.copy.return_value)
        mock_command.copy.assert_called_once_with()

    def test_add_listener(self):
        mock_listener = mock.Mock()
        component = tanjun.Component()

        result = component.add_listener(hikari.MessageCreateEvent, mock_listener)

        assert result is component
        assert mock_listener in component.listeners[hikari.MessageCreateEvent]

    def test_add_listener_when_other_listener_present(self):
        mock_listener = mock.Mock()
        mock_other_listener = mock.Mock()
        component = tanjun.Component().add_listener(hikari.MessageCreateEvent, mock_other_listener)

        result = component.add_listener(hikari.MessageCreateEvent, mock_listener)

        assert result is component
        assert mock_listener in component.listeners[hikari.MessageCreateEvent]
        assert mock_other_listener in component.listeners[hikari.MessageCreateEvent]

    def test_add_listener_when_client_bound(self):
        mock_listener = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client)

        result = component.add_listener(hikari.MessageCreateEvent, mock_listener)

        assert result is component
        assert mock_listener in component.listeners[hikari.MessageCreateEvent]
        mock_client.add_listener.assert_called_once_with(hikari.MessageCreateEvent, mock_listener)

    def test_add_listener_when_already_present(self):
        mock_listener = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client).add_listener(hikari.MessageCreateEvent, mock_listener)
        mock_client.reset_mock()

        result = component.add_listener(hikari.MessageCreateEvent, mock_listener)

        assert result is component
        assert list(component.listeners[hikari.MessageCreateEvent]).count(mock_listener) == 1
        mock_client.add_listener.assert_not_called()

    def test_remove_listener(self):
        mock_callback = mock.Mock()
        component = (
            tanjun.Component()
            .add_listener(hikari.MessageDeleteEvent, mock.Mock())
            .add_listener(hikari.MessageDeleteEvent, mock_callback)
        )

        result = component.remove_listener(hikari.MessageDeleteEvent, mock_callback)

        assert result is component
        assert mock_callback not in component.listeners[hikari.MessageDeleteEvent]

    def test_remove_listener_when_last_listener_for_event_type(self):
        mock_callback = mock.Mock()
        component = tanjun.Component().add_listener(hikari.GuildEvent, mock_callback)

        component.remove_listener(hikari.GuildEvent, mock_callback)
        assert hikari.GuildEvent not in component.listeners

    def test_remove_listener_when_client_bound(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        component = (
            tanjun.Component()
            .bind_client(mock_client)
            .add_listener(hikari.MessageDeleteEvent, mock.Mock())
            .add_listener(hikari.MessageDeleteEvent, mock_callback)
        )

        component.remove_listener(hikari.MessageDeleteEvent, mock_callback)

        assert mock_callback not in component.listeners[hikari.MessageDeleteEvent]
        mock_client.remove_listener.assert_called_once_with(hikari.MessageDeleteEvent, mock_callback)

    def test_remove_listener_when_event_type_not_found(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client)

        with pytest.raises(KeyError):
            component.remove_listener(hikari.MessageDeleteEvent, mock_callback)

        mock_client.remove_listener.assert_not_called()

    def test_remove_listener_when_listener_not_found(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        component = tanjun.Component().bind_client(mock_client).add_listener(hikari.MessageDeleteEvent, mock.Mock())

        with pytest.raises(ValueError, match=".+"):
            component.remove_listener(hikari.MessageDeleteEvent, mock_callback)

        mock_client.remove_listener.assert_not_called()

    def test_with_listener(self):
        add_listener = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent", (tanjun.Component,), exec_body=lambda ns: ns.update({"add_listener": add_listener})
        )()
        mock_listener = mock.Mock()

        result = component.with_listener(hikari.Event)(mock_listener)

        assert result is mock_listener
        add_listener.assert_called_once_with(hikari.Event, mock_listener)

    def test_add_on_close(self):
        mock_callback = mock.Mock()
        component = tanjun.Component()

        result = component.add_on_close(mock_callback)

        assert result is component
        assert component._on_close[0].callback is mock_callback

    def test_with_on_close(self):
        mock_add_on_close = mock.Mock()
        mock_callback = mock.Mock()

        class StubComponent(tanjun.Component):
            add_on_close = mock_add_on_close

        component = StubComponent()

        result = component.with_on_close(mock_callback)

        assert result is mock_callback
        mock_add_on_close.assert_called_once_with(mock_callback)

    def test_add_on_open(self):
        mock_callback = mock.Mock()
        component = tanjun.Component()

        result = component.add_on_open(mock_callback)

        assert result is component
        assert component._on_open[0].callback is mock_callback

    def test_with_on_open(self):
        mock_add_on_open = mock.Mock()
        mock_callback = mock.Mock()

        class StubComponent(tanjun.Component):
            add_on_open = mock_add_on_open

        component = StubComponent()

        result = component.with_on_open(mock_callback)

        assert result is mock_callback
        mock_add_on_open.assert_called_once_with(mock_callback)

    def test_bind_client(self):
        mock_client = mock.Mock()
        mock_message_command = mock.Mock()
        mock_other_message_command = mock.Mock()
        mock_slash_command = mock.Mock()
        mock_other_slash_command = mock.Mock()
        mock_listener = mock.Mock()
        mock_other_listener = mock.Mock()
        mock_callback = mock.Mock()
        mock_other_callback = mock.Mock()
        component = (
            tanjun.Component()
            .add_message_command(mock_message_command)
            .add_message_command(mock_other_message_command)
            .add_slash_command(mock_slash_command)
            .add_slash_command(mock_other_slash_command)
            .add_listener(hikari.ShardEvent, mock_listener)
            .add_listener(hikari.GuildEvent, mock_other_listener)
            .add_client_callback("a", mock_callback)
            .add_client_callback("b", mock_other_callback)
        )

        result = component.bind_client(mock_client)

        assert result is component
        assert component.client is mock_client
        mock_message_command.bind_client.assert_called_once_with(mock_client)
        mock_other_message_command.bind_client.assert_called_once_with(mock_client)
        mock_slash_command.bind_client.assert_called_once_with(mock_client)
        mock_other_slash_command.bind_client.assert_called_once_with(mock_client)
        mock_client.add_listener.assert_has_calls(
            [mock.call(hikari.ShardEvent, mock_listener), mock.call(hikari.GuildEvent, mock_other_listener)]
        )
        mock_client.add_client_callback.assert_has_calls(
            [mock.call("a", mock_callback), mock.call("b", mock_other_callback)]
        )

    def test_bind_client_when_already_bound(self):
        mock_client = mock.Mock()
        mock_message_command = mock.Mock()
        mock_slash_command = mock.Mock()
        component = (
            tanjun.Component()
            .bind_client(mock_client)
            .add_message_command(mock_message_command)
            .add_slash_command(mock_slash_command)
        )
        mock_client.reset_mock()
        mock_message_command.reset_mock()
        mock_slash_command.reset_mock()

        with pytest.raises(RuntimeError):
            component.bind_client(mock.Mock())

        mock_message_command.bind_client.assert_not_called()
        mock_slash_command.bind_client.assert_not_called()
        mock_client.add_listener.assert_not_called()
        mock_client.assert_not_called()

    def test_unbind_client(self):
        mock_client = mock.Mock(
            remove_listener=mock.Mock(side_effect=[None, ValueError, LookupError]),
            remove_client_callback=mock.Mock(side_effect=[None, ValueError, LookupError]),
        )
        mock_1st_listener = mock.Mock()
        mock_2nd_listener = mock.Mock()
        mock_3rd_listener = mock.Mock()
        mock_1st_callback = mock.Mock()
        mock_2nd_callback = mock.Mock()
        mock_3rd_callback = mock.Mock()
        component = (
            tanjun.Component()
            .add_listener(hikari.VoiceEvent, mock_1st_listener)
            .add_client_callback("32123", mock_1st_callback)
            .bind_client(mock_client)
            .add_listener(hikari.MemberEvent, mock_2nd_listener)
            .add_client_callback("3212222", mock_2nd_callback)
            .add_client_callback("321222", mock_3rd_callback)
            .add_listener(hikari.MemberEvent, mock_3rd_listener)
        )

        component.unbind_client(mock_client)

        assert component.client is None
        mock_client.remove_listener.assert_has_calls(
            [
                mock.call(hikari.VoiceEvent, mock_1st_listener),
                mock.call(hikari.MemberEvent, mock_2nd_listener),
                mock.call(hikari.MemberEvent, mock_3rd_listener),
            ]
        )
        mock_client.remove_client_callback.assert_has_calls(
            [
                mock.call("32123", mock_1st_callback),
                mock.call("3212222", mock_2nd_callback),
                mock.call("321222", mock_3rd_callback),
            ]
        )

    def test_unbind_client_when_not_bound(self):
        mock_client = mock.Mock()
        component = (
            tanjun.Component().add_listener(hikari.VoiceEvent, mock.Mock()).add_client_callback("32123", mock.Mock())
        )

        with pytest.raises(RuntimeError):
            component.unbind_client(mock_client)

        assert component.client is None
        mock_client.remove_listener.assert_not_called()
        mock_client.remove_client_callback.assert_not_called()

    def test_unbind_client_when_bound_to_different_client(self):
        mock_client = mock.Mock()
        mock_other_client = mock.Mock()
        component = (
            tanjun.Component()
            .bind_client(mock_client)
            .add_listener(hikari.VoiceEvent, mock.Mock())
            .add_client_callback("32123", mock.Mock())
        )

        with pytest.raises(RuntimeError):
            component.unbind_client(mock_other_client)

        assert component.client is mock_client
        mock_client.remove_listener.assert_not_called()
        mock_client.remove_client_callback.assert_not_called()
        mock_other_client.remove_listener.assert_not_called()
        mock_other_client.remove_client_callback.assert_not_called()

    def test_check_message_name(self):
        mock_other_command = mock.Mock(names=("yaa", "nooo"))
        mock_command = mock.Mock(names=("yamida is", "ok"))
        component = tanjun.Component().add_message_command(mock_other_command).add_message_command(mock_command)

        with mock.patch.object(
            tanjun.utilities, "match_prefix_names", side_effect=[None, "yamida is"]
        ) as match_prefix_names:
            result = component.check_message_name("yamida is gay")

            assert list(result) == [("yamida is", mock_command)]
            match_prefix_names.assert_has_calls(
                [
                    mock.call("yamida is gay", ("yaa", "nooo")),
                    mock.call("yamida is gay", ("yamida is", "ok")),
                ]
            )

    def test_check_message_name_when_not_found(self):
        component = (
            tanjun.Component()
            .add_message_command(mock.Mock(names=("yaa", "nooo")))
            .add_message_command(mock.Mock(names=("yamida is", "ok")))
        )

        with mock.patch.object(tanjun.utilities, "match_prefix_names", return_value=None) as match_prefix_names:
            result = component.check_message_name("yeeyt")

            assert list(result) == []
            match_prefix_names.assert_has_calls(
                [
                    mock.call("yeeyt", ("yaa", "nooo")),
                    mock.call("yeeyt", ("yamida is", "ok")),
                ]
            )

    def test_check_message_name_when_strict(self):
        mock_other_command = mock.Mock(names=("yaa", "nooo"))
        mock_command = mock.Mock(names=("a", "g", "d", "bro"))
        component = (
            tanjun.Component(strict=True).add_message_command(mock_command).add_message_command(mock_other_command)
        )

        with mock.patch.object(tanjun.utilities, "match_prefix_names") as match_prefix_names:
            result = component.check_message_name("bro no")

            assert list(result) == [("bro", mock_command)]
            match_prefix_names.assert_not_called()

    def test_check_message_name_when_strict_and_not_found(self):
        component = tanjun.Component(strict=True).add_message_command(mock.Mock(names=("a", "g", "d")))

        with mock.patch.object(tanjun.utilities, "match_prefix_names") as match_prefix_names:
            result = component.check_message_name("bro no")

            assert list(result) == []
            match_prefix_names.assert_not_called()

    def test_check_slash_name(self):
        mock_command = mock.Mock()
        mock_command.name = "test"
        assert list(tanjun.Component().add_slash_command(mock_command).check_slash_name("test")) == [mock_command]

    def test_check_slash_name_when_not_found(self):
        assert list(tanjun.Component().add_slash_command(mock.Mock()).check_slash_name("a")) == []

    @pytest.mark.skip(reason="TODO")
    def test_execute_interaction(self):
        ...  # includes _execute_interaction, and _check_context

    @pytest.mark.skip(reason="TODO")
    def test_execute_message(self):
        ...  # Includes _check_message_context and _check_context

    @pytest.mark.skip(reason="TODO")
    def test__load_from_properties(self):
        ...  # Should test this based on todo

    def test_add_schedule(self):
        mock_schedule = mock.Mock()
        component = tanjun.Component()

        result = component.add_schedule(mock_schedule)

        assert result is component
        assert component.schedules == [mock_schedule]
        mock_schedule.start.assert_not_called()

    def test_add_schedule_when_active(self):
        mock_schedule = mock.Mock()
        mock_client = mock.Mock(tanjun.Client)
        mock_loop = mock.Mock()
        component = tanjun.Component()
        component._client = mock_client
        component._loop = mock_loop

        result = component.add_schedule(mock_schedule)

        assert result is component
        assert component.schedules == [mock_schedule]
        mock_schedule.start.assert_called_once_with(mock_client, loop=mock_loop)

    def test_remove_schedule(self):
        mock_schedule = mock.Mock(is_alive=False)
        component = tanjun.Component().add_schedule(mock_schedule)
        assert mock_schedule in component.schedules

        result = component.remove_schedule(mock_schedule)

        assert result is component
        assert mock_schedule not in component.schedules
        mock_schedule.stop.assert_not_called()

    def test_remove_schedule_when_is_alive(self):
        mock_schedule = mock.Mock(is_alive=True)
        component = tanjun.Component().add_schedule(mock_schedule)
        assert mock_schedule in component.schedules

        result = component.remove_schedule(mock_schedule)

        assert result is component
        assert mock_schedule not in component.schedules
        mock_schedule.stop.assert_called_once_with()

    def test_with_schedule(self):
        add_schedule = mock.Mock()
        component: tanjun.Component = types.new_class(
            "StubComponent",
            (tanjun.Component,),
            exec_body=lambda ns: ns.update({"add_schedule": add_schedule}),
        )()
        mock_schedule = mock.Mock()

        result = component.with_schedule(mock_schedule)

        assert result is mock_schedule
        add_schedule.assert_called_once_with(mock_schedule)

    @pytest.mark.asyncio()
    async def test_close(self):
        mock_callback_1 = mock.AsyncMock()
        mock_callback_2 = mock.AsyncMock()
        mock_schedule_1 = mock.Mock(is_alive=True)
        mock_schedule_2 = mock.Mock(is_alive=True)
        mock_closed_schedule = mock.Mock(is_alive=False)
        mock_ctx_1 = mock.Mock()
        mock_ctx_2 = mock.Mock()
        mock_client = mock.Mock(tanjun.injecting.InjectorClient)
        mock_unbind = mock.Mock()
        component: tanjun.Component = (
            types.new_class(
                "StubComponent", (tanjun.Component,), exec_body=lambda b: b.update({"unbind_client": mock_unbind})
            )()
            .bind_client(mock_client)
            .add_schedule(mock_schedule_1)
            .add_schedule(mock_schedule_2)
            .add_schedule(mock_closed_schedule)
        )
        component._loop = mock.Mock()
        component._on_close = [mock_callback_1, mock_callback_2]

        with mock.patch.object(
            tanjun.injecting, "BasicInjectionContext", side_effect=[mock_ctx_1, mock_ctx_2]
        ) as basic_injection_context:
            await component.close()

        basic_injection_context.assert_has_calls([mock.call(mock_client), mock.call(mock_client)])
        mock_callback_1.resolve.assert_awaited_once_with(mock_ctx_1)
        mock_callback_2.resolve.assert_awaited_once_with(mock_ctx_2)
        mock_schedule_1.stop.assert_called_once_with()
        mock_schedule_2.stop.assert_called_once_with()
        mock_closed_schedule.stop.assert_not_called()
        mock_unbind.assert_not_called()
        assert component.loop is None

    @pytest.mark.asyncio()
    async def test_close_when_unbind(self):
        mock_callback_1 = mock.AsyncMock()
        mock_callback_2 = mock.AsyncMock()
        mock_schedule_1 = mock.Mock()
        mock_schedule_2 = mock.Mock()
        mock_ctx_1 = mock.Mock()
        mock_ctx_2 = mock.Mock()
        mock_client = mock.Mock(tanjun.injecting.InjectorClient)
        mock_unbind = mock.Mock()
        component: tanjun.Component = (
            types.new_class(
                "StubComponent", (tanjun.Component,), exec_body=lambda b: b.update({"unbind_client": mock_unbind})
            )()
            .bind_client(mock_client)
            .add_schedule(mock_schedule_1)
            .add_schedule(mock_schedule_2)
        )
        component._loop = mock.Mock()
        component._on_close = [mock_callback_1, mock_callback_2]

        with mock.patch.object(
            tanjun.injecting, "BasicInjectionContext", side_effect=[mock_ctx_1, mock_ctx_2]
        ) as basic_injection_context:
            await component.close(unbind=True)

        basic_injection_context.assert_has_calls([mock.call(mock_client), mock.call(mock_client)])
        mock_callback_1.resolve.assert_awaited_once_with(mock_ctx_1)
        mock_callback_2.resolve.assert_awaited_once_with(mock_ctx_2)
        mock_schedule_1.stop.assert_called_once_with()
        mock_schedule_2.stop.assert_called_once_with()
        mock_unbind.assert_called_once_with(mock_client)
        assert component.loop is None

    @pytest.mark.asyncio()
    async def test_close_when_not_active(self):
        component = tanjun.Component()

        with pytest.raises(RuntimeError, match="Component isn't active"):
            await component.close()

    @pytest.mark.asyncio()
    async def test_open(self):
        mock_callback_1 = mock.AsyncMock()
        mock_callback_2 = mock.AsyncMock()
        mock_schedule_1 = mock.Mock()
        mock_schedule_2 = mock.Mock()
        mock_ctx_1 = mock.Mock()
        mock_ctx_2 = mock.Mock()
        mock_client = mock.Mock(tanjun.injecting.InjectorClient)
        component = (
            tanjun.Component().bind_client(mock_client).add_schedule(mock_schedule_1).add_schedule(mock_schedule_2)
        )
        component._on_open = [mock_callback_1, mock_callback_2]

        stack = contextlib.ExitStack()
        basic_injection_context = stack.enter_context(
            mock.patch.object(tanjun.injecting, "BasicInjectionContext", side_effect=[mock_ctx_1, mock_ctx_2])
        )
        get_running_loop = stack.enter_context(mock.patch.object(asyncio, "get_running_loop"))

        with stack:
            await component.open()

        get_running_loop.assert_called_once_with()
        assert component.loop is get_running_loop.return_value
        basic_injection_context.assert_has_calls([mock.call(mock_client), mock.call(mock_client)])
        mock_callback_1.resolve.assert_awaited_once_with(mock_ctx_1)
        mock_callback_2.resolve.assert_awaited_once_with(mock_ctx_2)
        mock_schedule_1.start.assert_called_once_with(mock_client, loop=get_running_loop.return_value)
        mock_schedule_2.start.assert_called_once_with(mock_client, loop=get_running_loop.return_value)

    @pytest.mark.asyncio()
    async def test_open_when_already_active(self):
        component = tanjun.Component()
        component._loop = mock.Mock()

        with pytest.raises(RuntimeError, match="Component is already active"):
            await component.open()

    @pytest.mark.asyncio()
    async def test_open_when_not_client_bound(self):
        component = tanjun.Component()

        with pytest.raises(RuntimeError, match="Client isn't bound yet"):
            await component.open()

    def test_make_loader_has_load_property(self):
        assert tanjun.Component().make_loader(copy=False).has_load is True

    def test_make_loader_has_unload_property(self):
        assert tanjun.Component().make_loader(copy=False).has_unload is True

    def test_make_loader_load(self):
        component = tanjun.Component()
        loader = component.make_loader(copy=False)
        mock_client = mock.Mock()

        result = loader.load(mock_client)

        assert result is True
        mock_client.add_component.assert_called_once_with(component)

    def test_make_loader_load_when_copy(self):
        mock_copy = mock.Mock()
        mock_client = mock.Mock()

        class StubComponent(tanjun.Component):
            copy = mock_copy

        loader = StubComponent().make_loader(copy=True)

        loader.load(mock_client)
        mock_copy.assert_called_once_with()
        mock_client.add_component.assert_called_once_with(mock_copy.return_value)

    def test_make_loader_unload(self):
        mock_client = mock.Mock()
        loader = tanjun.Component(name="trans catgirls").make_loader()

        result = loader.unload(mock_client)

        assert result is True
        mock_client.remove_component_by_name.assert_called_once_with("trans catgirls")
