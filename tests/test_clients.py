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

import asyncio

# pyright: reportIncompatibleMethodOverride=none
# pyright: reportUnknownMemberType=none
# pyright: reportPrivateUsage=none
# This leads to too many false-positives around mocks.
import base64
import importlib
import pathlib
import random
import tempfile
import textwrap
import typing
from collections import abc as collections
from unittest import mock

import hikari
import pytest

import tanjun


class TestMessageAcceptsEnum:
    @pytest.mark.parametrize(
        ("value", "expected_type"),
        [
            (tanjun.MessageAcceptsEnum.ALL, hikari.MessageCreateEvent),
            (tanjun.MessageAcceptsEnum.DM_ONLY, hikari.DMMessageCreateEvent),
            (tanjun.MessageAcceptsEnum.GUILD_ONLY, hikari.GuildMessageCreateEvent),
            (tanjun.MessageAcceptsEnum.NONE, None),
        ],
    )
    def test_get_event_type(self, value: tanjun.MessageAcceptsEnum, expected_type: typing.Optional[hikari.Event]):
        assert value.get_event_type() == expected_type


class Test_LoaderDescriptor:
    def test_has_load_property(self):
        loader = tanjun.as_loader(mock.Mock())
        assert isinstance(loader, tanjun.clients._LoaderDescriptor)

        assert loader.has_load is True

    def test_has_unload_property(self):
        loader = tanjun.as_loader(mock.Mock())
        assert isinstance(loader, tanjun.clients._LoaderDescriptor)

        assert loader.has_unload is False

    def test___call__(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_loader(mock_callback)

        descriptor(1, "3", 3, a=31, e="43")  # type: ignore

        mock_callback.assert_called_once_with(1, "3", 3, a=31, e="43")

    def test_load(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock(tanjun.Client)
        descriptor = tanjun.as_loader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._LoaderDescriptor)

        result = descriptor.load(mock_client)

        assert result is True
        mock_callback.assert_called_once_with(mock_client)

    def test_load_when_must_be_std_and_not_std(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_loader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._LoaderDescriptor)

        with pytest.raises(ValueError, match="This loader requires instances of the standard Client implementation"):
            descriptor.load(mock.Mock())

        mock_callback.assert_not_called()

    def test_load_when_abc_allowed(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        descriptor = tanjun.as_loader(mock_callback, standard_impl=False)
        assert isinstance(descriptor, tanjun.clients._LoaderDescriptor)

        result = descriptor.load(mock_client)

        assert result is True
        mock_callback.assert_called_once_with(mock_client)

    def test_unload(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_loader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._LoaderDescriptor)

        result = descriptor.unload(mock.Mock(tanjun.Client))

        assert result is False
        mock_callback.assert_not_called()


class Test_UnloaderDescriptor:
    def test_has_load_property(self):
        loader = tanjun.as_unloader(mock.Mock())
        assert isinstance(loader, tanjun.clients._UnloaderDescriptor)

        assert loader.has_load is False

    def test_has_unload_property(self):
        loader = tanjun.as_unloader(mock.Mock())
        assert isinstance(loader, tanjun.clients._UnloaderDescriptor)

        assert loader.has_unload is True

    def test___call__(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_unloader(mock_callback)

        descriptor(1, "2", 3, a=31, b="312")  # type: ignore

        mock_callback.assert_called_once_with(1, "2", 3, a=31, b="312")

    def test_load(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_unloader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._UnloaderDescriptor)

        result = descriptor.load(mock.Mock(tanjun.Client))

        assert result is False
        mock_callback.assert_not_called()

    def test_unload(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock(tanjun.Client)
        descriptor = tanjun.as_unloader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._UnloaderDescriptor)

        result = descriptor.unload(mock_client)

        assert result is True
        mock_callback.assert_called_once_with(mock_client)

    def test_unload_when_must_be_std_and_not_std(self):
        mock_callback = mock.Mock()
        descriptor = tanjun.as_unloader(mock_callback)
        assert isinstance(descriptor, tanjun.clients._UnloaderDescriptor)

        with pytest.raises(ValueError, match="This unloader requires instances of the standard Client implementation"):
            descriptor.unload(mock.Mock())

        mock_callback.assert_not_called()

    def test_unload_when_abc_allowed(self):
        mock_callback = mock.Mock()
        mock_client = mock.Mock()
        descriptor = tanjun.as_unloader(mock_callback, standard_impl=False)
        assert isinstance(descriptor, tanjun.clients._UnloaderDescriptor)

        result = descriptor.unload(mock_client)

        assert result is True
        mock_callback.assert_called_once_with(mock_client)


class TestClient:
    @pytest.mark.skip(reason="TODO")
    def test___init__(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test___repr__(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_from_gateway_bot(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_from_rest_bot(self):
        ...

    @pytest.mark.asyncio()
    async def test_context_manager(self):
        open_ = mock.AsyncMock()
        close_ = mock.AsyncMock()

        class MockClient(tanjun.Client):
            open = open_
            close = close_

        async with MockClient(mock.Mock()):
            open_.assert_awaited_once_with()
            close_.assert_not_called()

        open_.assert_awaited_once_with()
        close_.assert_awaited_once_with()

    @pytest.mark.asyncio()
    async def test_async_context_manager(self) -> None:
        open_ = mock.AsyncMock()
        close_ = mock.AsyncMock()

        class StudClient(tanjun.Client):
            __slots__ = ()
            open = open_
            close = close_

        client = StudClient(mock.Mock())
        async with client:
            open_.assert_called_once_with()
            close_.assert_not_called()

        open_.assert_called_once_with()
        close_.assert_called_once_with()

    def test_message_accepts_property(self) -> None:
        client = tanjun.Client(mock.Mock(), events=mock.Mock()).set_message_accepts(tanjun.MessageAcceptsEnum.DM_ONLY)

        assert client.message_accepts is tanjun.MessageAcceptsEnum.DM_ONLY

    def test_is_human_only_property(self) -> None:
        client = tanjun.Client(mock.Mock()).set_human_only(True)

        assert client.is_human_only is True

    def test_cache_property(self) -> None:
        mock_cache = mock.Mock()
        client = tanjun.Client(mock.Mock(), cache=mock_cache)

        assert client.cache is mock_cache

    def test_events_property(self) -> None:
        mock_events = mock.Mock()
        client = tanjun.Client(mock.Mock(), events=mock_events)

        assert client.events is mock_events

    def test_defaults_to_ephemeral_property(self) -> None:
        assert tanjun.Client(mock.Mock()).defaults_to_ephemeral is False

    def test_hooks_property(self) -> None:
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock()).set_hooks(mock_hooks)

        assert client.hooks is mock_hooks

    def test_slash_hooks_property(self) -> None:
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock()).set_slash_hooks(mock_hooks)

        assert client.slash_hooks is mock_hooks

    def test_is_alive_property(self) -> None:
        client = tanjun.Client(mock.Mock())

        assert client.is_alive is False

    def test_loop_property(self) -> None:
        mock_loop = mock.Mock()
        client = tanjun.Client(mock.Mock())
        client._loop = mock_loop

        assert client.loop is mock_loop

    def test_message_hooks_property(self) -> None:
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock()).set_message_hooks(mock_hooks)

        assert client.message_hooks is mock_hooks

    def test_metadata_property(self) -> None:
        client = tanjun.Client(mock.Mock())
        client.metadata["a"] = 234
        client.metadata["555"] = 542

        assert client.metadata == {"a": 234, "555": 542}

    def test_prefix_getter_property(self) -> None:
        mock_callback = mock.Mock()
        assert tanjun.Client(mock.Mock()).set_prefix_getter(mock_callback).prefix_getter is mock_callback

    def test_prefix_getter_property_when_no_getter(self) -> None:
        assert tanjun.Client(mock.Mock()).prefix_getter is None

    def test_rest_property(self) -> None:
        mock_rest = mock.Mock()
        client = tanjun.Client(mock_rest)

        assert client.rest is mock_rest

    def test_server_property(self) -> None:
        mock_server = mock.Mock()
        client = tanjun.Client(mock.Mock, server=mock_server)

        assert client.server is mock_server

    def test_server_property_when_none(self) -> None:
        client = tanjun.Client(mock.Mock)

        assert client.server is None

    def test_shards_property(self) -> None:
        mock_shards = mock.Mock()
        client = tanjun.Client(mock.Mock(), shards=mock_shards)

        assert client.shards is mock_shards

    def test_shards_property_when_none(self) -> None:
        client = tanjun.Client(mock.Mock())

        assert client.shards is None

    def test_voice_property(self) -> None:
        mock_voice = mock.Mock()
        client = tanjun.Client(mock.Mock(), voice=mock_voice)

        assert client.voice is mock_voice

    def test_voice_property_when_none(self) -> None:
        client = tanjun.Client(mock.Mock())

        assert client.voice is None

    @pytest.mark.asyncio()
    async def test_declare_application_command_when_command_id_provided(self):
        rest = mock.AsyncMock()
        client = tanjun.Client(rest)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, 123321, application=54123, guild=65234)

        assert result is rest.edit_application_command.return_value
        rest.edit_application_command.assert_called_once_with(
            54123,
            123321,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        rest.create_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.asyncio()
    async def test_declare_application_command_when_command_id_provided_and_cached_app_id(self):
        rest = mock.AsyncMock()
        client = tanjun.Client(rest)
        client._cached_application_id = hikari.Snowflake(54123123)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, 123321, guild=65234)

        assert result is rest.edit_application_command.return_value
        rest.edit_application_command.assert_called_once_with(
            54123123,
            123321,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        rest.create_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.asyncio()
    async def test_declare_application_command_when_command_id_provided_fetchs_app_id(self):
        fetch_rest_application_id_ = mock.AsyncMock()

        class StubClient(tanjun.Client):
            fetch_rest_application_id = fetch_rest_application_id_

        rest = mock.AsyncMock()
        client = StubClient(rest)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, 123321, guild=65234)

        assert result is rest.edit_application_command.return_value
        rest.edit_application_command.assert_called_once_with(
            fetch_rest_application_id_.return_value,
            123321,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        fetch_rest_application_id_.assert_called_once_with()
        rest.create_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.asyncio()
    async def test_declare_application_command(self):
        rest = mock.AsyncMock()
        client = tanjun.Client(rest)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, application=54123, guild=65234)

        assert result is rest.create_application_command.return_value
        rest.create_application_command.assert_called_once_with(
            54123,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        rest.edit_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.asyncio()
    async def test_declare_application_command_when_cached_app_id(self):
        rest = mock.AsyncMock()
        client = tanjun.Client(rest)
        client._cached_application_id = hikari.Snowflake(54123123)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, guild=65234)

        assert result is rest.create_application_command.return_value
        rest.create_application_command.assert_called_once_with(
            54123123,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        rest.edit_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.asyncio()
    async def test_declare_application_command_fetchs_app_id(self):
        fetch_rest_application_id_ = mock.AsyncMock()

        class StubClient(tanjun.Client):
            fetch_rest_application_id = fetch_rest_application_id_

        rest = mock.AsyncMock()
        client = StubClient(rest)
        mock_command = mock.Mock()

        result = await client.declare_application_command(mock_command, guild=65234)

        assert result is rest.create_application_command.return_value
        rest.create_application_command.assert_called_once_with(
            fetch_rest_application_id_.return_value,
            guild=65234,
            name=mock_command.build.return_value.name,
            description=mock_command.build.return_value.description,
            options=mock_command.build.return_value.options,
        )
        fetch_rest_application_id_.assert_called_once_with()
        rest.edit_application_command.assert_not_called()
        mock_command.build.assert_called_once_with()
        mock_command.set_tracked_command.assert_not_called()

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_declare_application_commands(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_set_hikari_trait_injectors(self):
        ...

    def test_set_metadata(self):
        client = tanjun.Client(mock.Mock())
        key = mock.Mock()
        value = mock.Mock()

        result = client.set_metadata(key, value)

        assert result is client
        assert client.metadata[key] is value

    @pytest.mark.skip(reason="TODO")
    async def test_clear_commands(self):
        ...

    @pytest.mark.skip(reason="TODO")
    async def test_set_global_commands(self):
        ...

    @pytest.mark.skip(reason="TODO")
    async def test_declare_global_commands(self):
        ...

    def test_add_check(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.add_check(mock_check)

        assert result is client
        assert mock_check in client.checks

    def test_add_check_when_already_present(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check)

        result = client.add_check(mock_check)

        assert result is client
        assert list(client.checks).count(mock_check) == 1

    def test_remove_check(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check)

        result = client.remove_check(mock_check)

        assert result is client
        assert mock_check not in client.checks

    def test_remove_check_when_not_present(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock())

        with pytest.raises(ValueError, match=".+"):
            client.remove_check(mock_check)

        assert mock_check not in client.checks

    def test_with_check(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.with_check(mock_check)

        assert result is mock_check
        assert result in client.checks

    def test_with_check_when_already_present(self):
        mock_check = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check)

        result = client.with_check(mock_check)

        assert result is mock_check
        assert list(client.checks).count(mock_check) == 1

    @pytest.mark.asyncio()
    async def test_check(self):
        mock_check_1 = mock.Mock(return_value=True)
        mock_check_2 = mock.AsyncMock(return_value=True)
        mock_check_3 = mock.AsyncMock(return_value=True)
        mock_context = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check_1).add_check(mock_check_2).add_check(mock_check_3)

        assert await client.check(mock_context) is True

        mock_check_1.assert_called_once_with(mock_context)
        mock_check_2.assert_awaited_once_with(mock_context)
        mock_check_3.assert_awaited_once_with(mock_context)

    @pytest.mark.asyncio()
    async def test_check_when_one_returns_false(self):
        mock_check_1 = mock.Mock(return_value=True)
        mock_check_2 = mock.AsyncMock(return_value=False)
        mock_check_3 = mock.AsyncMock(return_value=True)
        mock_context = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check_1).add_check(mock_check_2).add_check(mock_check_3)

        assert await client.check(mock_context) is False

        mock_check_1.assert_called_once_with(mock_context)
        mock_check_2.assert_awaited_once_with(mock_context)
        mock_check_3.assert_awaited_once_with(mock_context)

    @pytest.mark.asyncio()
    async def test_check_when_one_raises(self):
        mock_check_1 = mock.Mock(return_value=True)
        mocK_exception = Exception("test")
        mock_check_2 = mock.AsyncMock(side_effect=mocK_exception)
        mock_check_3 = mock.AsyncMock(return_value=True)
        mock_context = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check_1).add_check(mock_check_2).add_check(mock_check_3)

        with pytest.raises(Exception, match="test") as exc:
            await client.check(mock_context)

        assert exc.value is mocK_exception

        mock_check_1.assert_called_once_with(mock_context)
        mock_check_2.assert_awaited_once_with(mock_context)
        mock_check_3.assert_awaited_once_with(mock_context)

    @pytest.mark.asyncio()
    async def test_check_when_one_raises_failed_check(self):
        mock_check_1 = mock.Mock(return_value=True)
        mock_check_2 = mock.AsyncMock(side_effect=tanjun.FailedCheck())
        mock_check_3 = mock.AsyncMock(return_value=True)
        mock_context = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_check(mock_check_1).add_check(mock_check_2).add_check(mock_check_3)

        assert await client.check(mock_context) is False

        mock_check_1.assert_called_once_with(mock_context)
        mock_check_2.assert_awaited_once_with(mock_context)
        mock_check_3.assert_awaited_once_with(mock_context)

    @pytest.mark.skip(reason="TODO")
    def test_add_component(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_component_when_already_present(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_component_when_add_injector(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_component_when_is_alive(self):
        ...

    def test_get_component_by_name(self):
        mock_component = mock.Mock()
        mock_component.name = "vader"
        client = (
            tanjun.Client(mock.Mock())
            .add_component(mock.Mock())
            .add_component(mock_component)
            .add_component(mock.Mock())
        )

        assert client.get_component_by_name("vader") is mock_component

    def test_get_component_by_name_when_not_present(self):
        assert tanjun.Client(mock.AsyncMock()).get_component_by_name("test") is None

    @pytest.mark.skip(reason="TODO")
    def test_remove_component(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_component_when_not_present(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_component_when_is_alive(self):
        ...

    def test_remove_component_by_name(self):
        remove_component_ = mock.Mock()

        class StubClient(tanjun.Client):
            remove_component = remove_component_

        mock_component = mock.Mock()
        mock_component.name = "aye"
        client = StubClient(mock.AsyncMock).add_component(mock.Mock()).add_component(mock_component)
        remove_component_.return_value = client

        result = client.remove_component_by_name("aye")

        assert result is client
        remove_component_.assert_called_once_with(mock_component)

    def test_remove_component_by_name_when_not_present(self):
        client = tanjun.Client(mock.AsyncMock())

        with pytest.raises(KeyError):
            client.remove_component_by_name("nyan")

    @pytest.mark.skip(reason="TODO")
    def test_add_client_callback(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_client_callback_when_already_present(self):
        ...

    @pytest.mark.asyncio()
    async def test_dispatch_client_callback(self):
        ...

    @pytest.mark.asyncio()
    async def test_dispatch_client_callback_when_name_not_found(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_get_client_callbacks(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_get_client_callbacks_when_name_not_found(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_client_callback(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_client_callback_when_name_not_found(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_client_callback_when_callback_not_found(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_remove_client_callback_when_last_callback(self):
        ...

    def test_with_client_callback(self):
        add_client_callback_ = mock.Mock()

        class StubClient(tanjun.Client):
            add_client_callback = add_client_callback_

        client = StubClient(mock.Mock())
        add_client_callback_.reset_mock()
        mock_callback = mock.Mock()

        result = client.with_client_callback("aye")(mock_callback)

        assert result is mock_callback
        add_client_callback_.assert_called_once_with("aye", mock_callback)

    @pytest.mark.skip(reason="TODO")
    def test_add_listener(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_listener_when_already_present(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_listener_when_alive(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_listener_when_alive_and_events(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_add_listener_when_events(self):
        ...

    def test_remove_listener(self):
        mock_callback = mock.Mock()
        client = (
            tanjun.Client(mock.Mock())
            .add_listener(hikari.GuildTypingEvent, mock_callback)
            .add_listener(hikari.GuildTypingEvent, mock.Mock())
        )

        result = client.remove_listener(hikari.GuildTypingEvent, mock_callback)

        assert result is client
        assert mock_callback not in client.listeners[hikari.GuildTypingEvent]

    def test_remove_listener_when_event_type_not_present(self):
        client = tanjun.Client(mock.Mock())

        with pytest.raises(KeyError):
            client.remove_listener(hikari.GuildTypingEvent, mock.Mock())

    def test_remove_listener_when_callback_not_present(self):
        mock_other_callback = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_listener(hikari.GuildTypingEvent, mock_other_callback)

        with pytest.raises(ValueError, match=".+"):
            client.remove_listener(hikari.GuildTypingEvent, mock.Mock())

        assert client.listeners[hikari.GuildTypingEvent] == [mock_other_callback]

    def test_remove_listener_when_last_listener(self):
        mock_callback = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_listener(hikari.RoleEvent, mock_callback)

        client.remove_listener(hikari.RoleEvent, mock_callback)

        assert hikari.RoleEvent not in client.listeners

    def test_remove_listener_when_alive(self):
        mock_callback = mock.Mock()
        client = tanjun.Client(mock.Mock()).add_listener(hikari.RoleEvent, mock_callback)
        client._loop = mock.Mock()

        client.remove_listener(hikari.RoleEvent, mock_callback)

        assert hikari.RoleEvent not in client.listeners

    def test_remove_listener_when_alive_and_events(self):
        mock_events = mock.Mock()
        mock_callback = mock.Mock()

        with mock.patch.object(tanjun.injecting, "SelfInjectingCallback") as self_injecting_callback:
            client = tanjun.Client(mock.Mock(), events=mock_events, event_managed=False).add_listener(
                hikari.RoleEvent, mock_callback
            )
            client._loop = mock.Mock()

            client.remove_listener(hikari.RoleEvent, self_injecting_callback.return_value)

        assert hikari.RoleEvent not in client.listeners
        mock_events.unsubscribe.assert_called_once_with(hikari.RoleEvent, self_injecting_callback.return_value.__call__)

    def test_remove_listener_when_events(self):
        mock_events = mock.Mock()
        mock_callback = mock.Mock()
        client = tanjun.Client(mock.Mock(), events=mock_events, event_managed=False).add_listener(
            hikari.RoleEvent, mock_callback
        )

        client.remove_listener(hikari.RoleEvent, mock_callback)

        assert hikari.RoleEvent not in client.listeners
        mock_events.unsubscribe.assert_not_called()

    def test_with_listener(self):
        add_listener_ = mock.Mock()

        class StubClient(tanjun.Client):
            add_listener = add_listener_

        client = StubClient(mock.Mock())
        mock_callback = mock.Mock()

        result = client.with_listener(hikari.GuildAvailableEvent)(mock_callback)

        assert result is mock_callback
        add_listener_.assert_called_once_with(hikari.GuildAvailableEvent, mock_callback)

    def test_add_prefix(self):
        client = tanjun.Client(mock.Mock())

        result = client.add_prefix("aye")

        assert result is client
        assert "aye" in client.prefixes

    def test_add_prefix_when_already_present(self):
        client = tanjun.Client(mock.Mock()).add_prefix("lmao")

        result = client.add_prefix("lmao")

        assert result is client
        list(client.prefixes).count("lmao") == 1

    def test_add_prefix_when_iterable(self):
        client = tanjun.Client(mock.Mock())

        result = client.add_prefix(["Grand", "dad", "FNAF"])

        assert result is client
        assert list(client.prefixes).count("Grand") == 1
        assert list(client.prefixes).count("dad") == 1
        assert list(client.prefixes).count("FNAF") == 1

    def test_add_prefix_when_iterable_and_already_present(self):
        client = tanjun.Client(mock.Mock()).add_prefix(["naye", "laala", "OBAMA"])

        result = client.add_prefix(["naye", "OBAMA", "bourg"])

        assert result is client
        assert list(client.prefixes).count("naye") == 1
        assert list(client.prefixes).count("laala") == 1
        assert list(client.prefixes).count("OBAMA") == 1
        assert list(client.prefixes).count("bourg") == 1

    def test_remove_prefix(self):
        client = tanjun.Client(mock.Mock()).add_prefix("lmao")

        result = client.remove_prefix("lmao")

        assert result is client
        assert "lmao" not in client.prefixes

    def test_remove_prefix_when_not_present(self):
        client = tanjun.Client(mock.Mock())

        with pytest.raises(ValueError, match=".+"):
            client.remove_prefix("lmao")

    def test_set_prefix_getter(self):
        mock_getter = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.set_prefix_getter(mock_getter)

        assert result is client
        assert client.prefix_getter is mock_getter

    def test_set_prefix_getter_when_none(self):
        client = tanjun.Client(mock.Mock()).set_prefix_getter(mock.Mock())

        result = client.set_prefix_getter(None)

        assert result is client
        assert client.prefix_getter is None

    def test_with_prefix_getter(self):
        mock_getter = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.with_prefix_getter(mock_getter)

        assert result is mock_getter
        assert client.prefix_getter is mock_getter

    def test_iter_commands(self):
        mock_slash_1 = mock.Mock()
        mock_slash_2 = mock.Mock()
        mock_slash_3 = mock.Mock()

        mock_message_1 = mock.Mock()
        mock_message_2 = mock.Mock()
        mock_message_3 = mock.Mock()
        mock_message_4 = mock.Mock()
        client = (
            tanjun.Client(mock.Mock())
            .add_component(mock.Mock(message_commands=[mock_message_1], slash_commands=[mock_slash_1]))
            .add_component(mock.Mock(message_commands=[mock_message_2], slash_commands=[]))
            .add_component(mock.Mock(message_commands=[mock_message_3], slash_commands=[mock_slash_2, mock_slash_3]))
            .add_component(mock.Mock(message_commands=[], slash_commands=[]))
            .add_component(mock.Mock(message_commands=[mock_message_4], slash_commands=[]))
        )

        commands = list(client.iter_commands())

        assert commands == [
            mock_message_1,
            mock_message_2,
            mock_message_3,
            mock_message_4,
            mock_slash_1,
            mock_slash_2,
            mock_slash_3,
        ]

    def test_iter_message_commands(self):
        mock_command_1 = mock.Mock()
        mock_command_2 = mock.Mock()
        mock_command_3 = mock.Mock()
        mock_command_4 = mock.Mock()
        mock_command_5 = mock.Mock()
        client = (
            tanjun.Client(mock.Mock())
            .add_component(mock.Mock(slash_commands=[]))
            .add_component(mock.Mock(slash_commands=[mock_command_1, mock_command_2]))
            .add_component(mock.Mock(slash_commands=[]))
            .add_component(mock.Mock(slash_commands=[mock_command_3, mock_command_4]))
            .add_component(mock.Mock(slash_commands=[mock_command_5]))
        )

        commands = list(client.iter_slash_commands())

        assert commands == [mock_command_1, mock_command_2, mock_command_3, mock_command_4, mock_command_5]

    def test_iter_slash_commands(self):
        mock_command_1 = mock.Mock()
        mock_command_2 = mock.Mock()
        mock_command_3 = mock.Mock()
        mock_command_4 = mock.Mock()
        mock_command_5 = mock.Mock()
        client = (
            tanjun.Client(mock.Mock())
            .add_component(mock.Mock(slash_commands=[mock_command_1, mock_command_2]))
            .add_component(mock.Mock(slash_commands=[]))
            .add_component(mock.Mock(slash_commands=[mock_command_3, mock_command_4]))
            .add_component(mock.Mock(slash_commands=[]))
            .add_component(mock.Mock(slash_commands=[mock_command_5]))
        )

        commands = list(client.iter_slash_commands())

        assert commands == [mock_command_1, mock_command_2, mock_command_3, mock_command_4, mock_command_5]

    def test_iter_slash_commands_when_global_only(self):
        mock_command_1 = mock.Mock(is_global=True)
        mock_command_2 = mock.Mock(is_global=True)
        mock_command_3 = mock.Mock(is_global=True)
        mock_command_4 = mock.Mock(is_global=True)
        client = (
            tanjun.Client(mock.Mock())
            .add_component(mock.Mock(slash_commands=[mock_command_1, mock_command_2]))
            .add_component(mock.Mock(slash_commands=[]))
            .add_component(mock.Mock(slash_commands=[mock.Mock(is_global=False), mock.Mock(is_global=False)]))
            .add_component(mock.Mock(slash_commands=[mock.Mock(is_global=False), mock_command_3]))
            .add_component(mock.Mock(slash_commands=[mock_command_4]))
        )

        commands = list(client.iter_slash_commands(global_only=True))

        assert commands == [mock_command_1, mock_command_2, mock_command_3, mock_command_4]

    @pytest.mark.skip(reason="TODO")
    def test_check_message_name(self):
        ...

    @pytest.mark.skip(reason="TODO")
    def test_check_slash_name(self):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_close(self):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_open(self):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_fetch_rest_application_id(self):
        ...

    def test_set_hooks(self):
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.set_hooks(mock_hooks)

        assert result is client
        assert client.hooks is mock_hooks

    def test_set_hooks_when_none(self):
        client = tanjun.Client(mock.Mock()).set_hooks(mock.Mock())

        result = client.set_hooks(None)

        assert result is client
        assert client.hooks is None

    def test_set_ephemeral_default(self):
        client = tanjun.Client(mock.Mock())

        result = client.set_ephemeral_default(True)

        assert result is client
        assert client.defaults_to_ephemeral is True

    def test_set_slash_hooks(self):
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.set_slash_hooks(mock_hooks)

        assert result is client
        assert client.slash_hooks is mock_hooks

    def test_set_slash_hooks_when_none(self):
        client = tanjun.Client(mock.Mock()).set_slash_hooks(mock.Mock())

        result = client.set_slash_hooks(None)

        assert result is client
        assert client.slash_hooks is None

    def test_set_message_hooks(self):
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock())

        result = client.set_message_hooks(mock_hooks)

        assert result is client
        assert client.message_hooks is mock_hooks

    def test_set_message_hooks_when_none(self):
        client = tanjun.Client(mock.Mock()).set_message_hooks(mock.Mock())

        result = client.set_message_hooks(None)

        assert result is client
        assert client.message_hooks is None

    @pytest.fixture()
    def file(self) -> collections.Iterator[typing.IO[str]]:
        # A try, finally is used to delete the file rather than relying on delete=True behaviour
        # as on Windows the file cannot be accessed by other processes if delete is True.
        file = tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False)
        try:
            with file:
                yield file

        finally:
            pathlib.Path(file.name).unlink(missing_ok=False)

    def test__load_modules_with_system_path(self, file: typing.IO[str]):
        add_component_ = mock.Mock()
        add_client_callback_ = mock.Mock()

        class MockClient(tanjun.Client):
            add_component = add_component_

            add_client_callback = add_client_callback_

        client = MockClient(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                import tanjun

                @tanjun.as_loader
                def __dunder_loader__(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(5533)
                    client.add_client_callback(554444)

                foo = 5686544536876
                bar = object()

                @tanjun.as_loader
                def load_module(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(123)
                    client.add_client_callback(4312)

                class FullMetal:
                    ...

                @tanjun.as_loader
                def _load_module(client: tanjun.abc.Client) -> None:
                    assert False
                    client.add_component(5432)
                    client.add_client_callback(6543456)
                """
            )
        )
        file.flush()

        generator = client._load_module(pathlib.Path(file.name))
        module = next(generator)()
        try:
            generator.send(module)

        except StopIteration:
            pass

        else:
            pytest.fail("Expected StopIteration")

        add_component_.assert_has_calls([mock.call(5533), mock.call(123)])
        add_client_callback_.assert_has_calls([mock.call(554444), mock.call(4312)])

    def test__load_modules_with_system_path_respects_all(self, file: typing.IO[str]):
        add_component_ = mock.Mock()
        add_client_callback_ = mock.Mock()

        class MockClient(tanjun.Client):
            add_component = add_component_

            add_client_callback = add_client_callback_

        client = MockClient(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                __all__ = ["FullMetal", "load_module", "_priv_load", "bar", "foo","easy", "tanjun", "missing"]
                import tanjun

                foo = 5686544536876
                bar = object()

                @tanjun.as_loader
                def _priv_load(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(777)
                    client.add_client_callback(778)

                class FullMetal:
                    ...

                @tanjun.as_loader
                def load_module(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(123)
                    client.add_client_callback(4312)

                @tanjun.as_loader
                def easy(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(5432)
                    client.add_client_callback(6543456)

                @tanjun.as_loader
                def not_in_all(client: tanjun.abc.Client) -> None:
                    assert False
                """
            )
        )
        file.flush()

        generator = client._load_module(pathlib.Path(file.name))
        module = next(generator)()
        try:
            generator.send(module)

        except StopIteration:
            pass

        else:
            pytest.fail("Expected StopIteration")

        add_component_.assert_has_calls([mock.call(123), mock.call(777), mock.call(5432)])
        add_client_callback_.assert_has_calls([mock.call(4312), mock.call(778), mock.call(6543456)])

    def test__load_modules_with_system_path_when_all_and_no_loaders_found(self, file: typing.IO[str]):
        add_component_ = mock.Mock()
        add_client_callback_ = mock.Mock()

        class MockClient(tanjun.Client):
            add_component = add_component_

            add_client_callback = add_client_callback_

        client = MockClient(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                __all__ = ["tanjun", "foo", "missing", "bar", "load_module", "FullMetal"]

                import tanjun

                foo = 5686544536876
                bar = object()

                def load_module(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(123)
                    client.add_client_callback(4312)

                class FullMetal:
                    ...

                @tanjun.as_loader
                def not_in_all(client: tanjun.abc.Client) -> None:
                    assert False
                """
            )
        )
        file.flush()
        generator = client._load_module(pathlib.Path(file.name))
        module = next(generator)()

        with pytest.raises(tanjun.ModuleMissingLoaders):
            generator.send(module)

    def test__load_modules_with_system_path_when_no_loaders_found(self, file: typing.IO[str]):
        add_component_ = mock.Mock()
        add_client_callback_ = mock.Mock()

        class MockClient(tanjun.Client):
            add_component = add_component_

            add_client_callback = add_client_callback_

        client = MockClient(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                import tanjun

                foo = 5686544536876
                bar = object()

                def load_module(client: tanjun.abc.Client) -> None:
                    assert isinstance(client, tanjun.Client)
                    client.add_component(123)
                    client.add_client_callback(4312)

                class FullMetal:
                    ...
                """
            )
        )
        file.flush()
        generator = client._load_module(pathlib.Path(file.name))
        module = next(generator)()

        with pytest.raises(tanjun.ModuleMissingLoaders):
            generator.send(module)

    def test__load_modules_with_system_path_when_loader_raises(self, file: typing.IO[str]):
        add_component_ = mock.Mock()
        add_client_callback_ = mock.Mock()

        class MockClient(tanjun.Client):
            add_component = add_component_

            add_client_callback = add_client_callback_

        client = MockClient(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                import tanjun

                foo = 5686544536876
                bar = object()

                @tanjun.as_loader
                def load_module(client: tanjun.abc.Client) -> None:
                    raise RuntimeError("Mummy uwu")

                class FullMetal:
                    ...
                """
            )
        )
        file.flush()
        generator = client._load_module(pathlib.Path(file.name))
        module = next(generator)()

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            generator.send(module)

        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert exc_info.value.__cause__.args == ("Mummy uwu",)

    def test__load_modules_with_system_path_when_already_loaded(self, file: typing.IO[str]):
        client = tanjun.Client(mock.AsyncMock())
        file.write(textwrap.dedent("""raise NotImplementedError("This shouldn't ever be imported")"""))
        file.flush()
        path = pathlib.Path(file.name)
        client._path_modules[path] = mock.Mock()
        generator = client._load_module(pathlib.Path(file.name))

        with pytest.raises(tanjun.ModuleStateConflict):
            next(generator)

    def test__load_modules_with_system_path_for_unknown_path(self):
        class MockClient(tanjun.Client):
            add_component = mock.Mock()
            add_client_callback = mock.Mock()

        client = MockClient(mock.AsyncMock())
        random_path = pathlib.Path(base64.urlsafe_b64encode(random.randbytes(64)).decode())
        generator = client._load_module(random_path)
        next_ = next(generator)

        with pytest.raises(ModuleNotFoundError):
            next_()

    def test__load_modules_with_python_module_path(self):
        client = tanjun.Client(mock.AsyncMock())
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True))

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=False)),
            no=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True)),
            _priv_loader=priv_loader,
            __all__=None,
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            generator = client._load_module("okokok.no.u")
            module = next(generator)()
            try:
                generator.send(module)

            except StopIteration:
                pass

            else:
                pytest.fail("Expected StopIteration")

            import_module.assert_called_once_with("okokok.no.u")

        mock_module.loader.load.assert_called_once_with(client)
        mock_module.other_loader.load.assert_called_once_with(client)
        priv_loader.load.assert_not_called()

    def test__load_modules_with_python_module_path_respects_all(self):
        client = tanjun.Client(mock.AsyncMock())
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True))

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True)),
            no=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=False)),
            _priv_loader=priv_loader,
            another_loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True)),
            __all__=["loader", "_priv_loader", "another_loader", "missing"],
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            generator = client._load_module("okokok.no.u")
            module = next(generator)()
            try:
                generator.send(module)

            except StopIteration:
                pass

            else:
                pytest.fail("Expected StopIteration")

            import_module.assert_called_once_with("okokok.no.u")

        mock_module.loader.load.assert_called_once_with(client)
        mock_module.other_loader.load.assert_not_called()
        priv_loader.load.assert_called_once_with(client)
        mock_module.another_loader.load.assert_called_once_with(client)

    def test__load_modules_with_python_module_path_when_no_loader_found(self):
        client = tanjun.Client(mock.AsyncMock())
        mock_module = mock.Mock(
            object=123,
            foo="ok",
            no=object(),
            __all__=None,
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=False)),
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            generator = client._load_module("okokok.no.u")
            module = next(generator)()

            with pytest.raises(tanjun.ModuleMissingLoaders):
                generator.send(module)

            import_module.assert_called_once_with("okokok.no.u")

        mock_module.loader.load.assert_called_once_with(client)

    def test__load_modules_with_python_module_path_when_loader_raises(self):
        mock_exception = KeyError("ayayaya")
        mock_module = mock.Mock(
            foo=5686544536876, bar=object(), load_module=mock.Mock(tanjun.abc.ClientLoader, has_load=True)
        )
        mock_module.load_module.load.side_effect = mock_exception

        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=mock_module):
            generator = client._load_module("e")
            module = next(generator)()

            with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
                generator.send(module)

        exc_info.value.__cause__ is mock_exception

    def test__load_modules_with_python_module_path_when_already_loaded(self):
        client = tanjun.Client(mock.AsyncMock())
        client._modules["ayayayaya.ok"] = mock.Mock()
        generator = client._load_module("ayayayaya.ok")

        with pytest.raises(tanjun.ModuleStateConflict):
            next(generator)

    def test_load_modules(self):
        mock_path = mock.Mock(pathlib.Path)
        mock_gen_1 = mock.Mock(__next__=mock.Mock())
        mock_gen_1.send.side_effect = StopIteration
        mock_gen_2 = mock.Mock(__next__=mock.Mock())
        mock_gen_2.send.side_effect = StopIteration
        mock__load_module = mock.Mock(side_effect=[mock_gen_1, mock_gen_2])

        class StubClient(tanjun.Client):
            _load_module = mock__load_module

        client = StubClient(mock.AsyncMock())

        result = client.load_modules(mock_path, "ok.no.u")

        assert result is client
        mock__load_module.assert_has_calls([mock.call(mock_path.absolute.return_value), mock.call("ok.no.u")])
        mock_path.absolute.assert_called_once_with()
        mock_gen_1.__next__.assert_called_once_with()
        mock_gen_1.__next__.return_value.assert_called_once_with()
        mock_gen_1.send.assert_called_once_with(mock_gen_1.__next__.return_value.return_value)
        mock_gen_2.__next__.assert_called_once_with()
        mock_gen_2.__next__.return_value.assert_called_once_with()
        mock_gen_2.send.assert_called_once_with(mock_gen_2.__next__.return_value.return_value)

    def test_load_modules_when_module_import_raises(self):
        mock_exception = ValueError("aye")
        mock_gen = mock.Mock(__next__=mock.Mock())
        mock_gen.__next__.return_value.side_effect = mock_exception

        mock__load_module = mock.Mock(return_value=mock_gen)

        class StubClient(tanjun.Client):
            _load_module = mock__load_module

        client = StubClient(mock.AsyncMock())

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            client.load_modules("ok.no.u")

        assert exc_info.value.__cause__ is mock_exception

        mock__load_module.assert_called_once_with("ok.no.u")
        mock_gen.__next__.assert_called_once_with()
        mock_gen.__next__.return_value.assert_called_once_with()
        mock_gen.send.assert_not_called()

    @mock.patch.object(asyncio, "get_running_loop")
    @pytest.mark.asyncio()
    async def test_load_modules_async(self, get_running_loop: mock.Mock):
        mock_executor_result_1 = mock.Mock()
        mock_executor_result_2 = mock.Mock()
        mock_executor_result_3 = mock.Mock()
        get_running_loop.return_value.run_in_executor = mock.AsyncMock(
            side_effect=[mock_executor_result_1, mock_executor_result_2, mock_executor_result_3]
        )
        mock_path = mock.Mock(pathlib.Path)
        mock_gen_1 = mock.Mock(__next__=mock.Mock())
        mock_gen_1.send.side_effect = StopIteration
        mock_gen_2 = mock.Mock(__next__=mock.Mock())
        mock_gen_2.send.side_effect = StopIteration
        mock__load_module = mock.Mock(side_effect=[mock_gen_1, mock_gen_2])

        class StubClient(tanjun.Client):
            _load_module = mock__load_module

        client = StubClient(mock.AsyncMock())

        result = await client.load_modules_async(mock_path, "ok.no.u")

        assert result is None
        mock__load_module.assert_has_calls([mock.call(mock_executor_result_1), mock.call("ok.no.u")])
        mock_gen_1.__next__.assert_called_once_with()
        mock_gen_1.send.assert_called_once_with(mock_executor_result_2)
        mock_gen_2.__next__.assert_called_once_with()
        mock_gen_2.send.assert_called_once_with(mock_executor_result_3)
        get_running_loop.assert_called_once_with()
        get_running_loop.return_value.run_in_executor.assert_has_calls(
            [
                mock.call(None, mock_path.absolute),
                mock.call(None, mock_gen_1.__next__.return_value),
                mock.call(None, mock_gen_2.__next__.return_value),
            ]
        )

    @mock.patch.object(asyncio, "get_running_loop")
    @pytest.mark.asyncio()
    async def test_load_modules_async_when_module_import_raises(self, get_running_loop: mock.Mock):
        mock_exception = ValueError("aye")
        mock_gen = mock.Mock(__next__=mock.Mock())
        get_running_loop.return_value.run_in_executor = mock.AsyncMock(side_effect=mock_exception)
        mock__load_module = mock.Mock(return_value=mock_gen)

        class StubClient(tanjun.Client):
            _load_module = mock__load_module

        client = StubClient(mock.AsyncMock())

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            await client.load_modules_async("ok.no.u")

        assert exc_info.value.__cause__ is mock_exception

        mock__load_module.assert_called_once_with("ok.no.u")
        mock_gen.__next__.assert_called_once_with()
        get_running_loop.return_value.run_in_executor.assert_called_once_with(None, mock_gen.__next__.return_value)
        mock_gen.send.assert_not_called()

    def test_unload_modules_with_system_path(self):
        priv_unloader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            __dunder_loader__=mock.Mock(tanjun.abc.ClientLoader),
            foo=5686544536876,
            bar=object(),
            unload_module=mock.Mock(tanjun.abc.ClientLoader),
            FullMetal=object,
            _unload_modules=priv_unloader,
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path("aye")
        client._path_modules[path.absolute()] = old_module

        result = client.unload_modules(path)

        assert result is client
        old_module.__dunder_loader__.unload.assert_called_once_with(client)
        old_module.unload_module.unload.assert_called_once_with(client)
        priv_unloader.unload.assert_not_called()
        assert path.absolute() not in client._path_modules

    def test_unload_modules_with_system_path_respects_all(self):
        priv_unload = mock.Mock(tanjun.abc.ClientLoader)
        mock_module = mock.Mock(
            __all__=["FullMetal", "_priv_unload", "unload_module", "_bar", "foo", "load_module", "missing"],
            foo=5686544536876,
            _bar=object(),
            _priv_unload=priv_unload,
            FullMetal=object(),
            unload_module=mock.Mock(tanjun.abc.ClientLoader),
            load_module=mock.Mock(tanjun.abc.ClientLoader),
            not_in_all=mock.Mock(tanjun.abc.ClientLoader),
        )

        path = pathlib.Path("ayeeeee")
        client = tanjun.Client(mock.AsyncMock())
        client._path_modules[path.absolute()] = mock_module

        client.unload_modules(path)

        priv_unload.unload.assert_called_once_with(client)
        mock_module.unload_module.unload.assert_called_once_with(client)
        mock_module.load_module.unload.assert_called_once_with(client)
        mock_module.not_in_all.unload.assert_not_called()
        assert path.absolute() not in client._path_modules

    def test_unload_modules_with_system_path_when_not_loaded(self):
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path("naye")

        with pytest.raises(tanjun.ModuleStateConflict):
            client.unload_modules(path)

        assert path.absolute() not in client._path_modules

    def test_unload_modules_with_system_path_when_no_unloaders_found(self):
        mock_module = mock.Mock(
            foo=5686544536876,
            bar=object(),
            FullMetal=object,
            load_module=mock.Mock(tanjun.abc.ClientLoader, has_unload=False, unload=mock.Mock(return_value=False)),
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path("rewwewew")
        client._path_modules[path.absolute()] = mock_module

        with pytest.raises(tanjun.ModuleMissingLoaders):
            client.unload_modules(path)

        assert client._path_modules[path.absolute()] is mock_module

    def test_unload_modules_with_system_path_when_all_and_no_unloaders_found(self):
        mock_module = mock.Mock(
            __all__=["FullMetal", "bar", "foo", "load_module", "missing"],
            foo=5686544536876,
            bar=object(),
            FullMetal=int,
            load_module=mock.Mock(tanjun.abc.ClientLoader, has_unload=False, unload=mock.Mock(return_value=False)),
            unload_module=mock.Mock(tanjun.abc.ClientLoader, has_unload=True, unload=mock.Mock(return_value=True)),
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path("./123dsaasd")
        client._path_modules[path.absolute()] = mock_module

        with pytest.raises(tanjun.ModuleMissingLoaders):
            client.unload_modules(path)

        assert client._path_modules[path.absolute()] is mock_module

    def test_unload_modules_with_system_path_when_unloader_raises(self):
        mock_exception = ValueError("aye")
        mock_module = mock.Mock(
            foo=5686544536876,
            bar=object(),
            FullMetal=str,
            load_module=mock.Mock(tanjun.abc.ClientLoader, has_unload=True, unload=mock.Mock(return_value=True)),
            unload_module=mock.Mock(
                tanjun.abc.ClientLoader, has_unload=True, unload=mock.Mock(side_effect=mock_exception)
            ),
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path("./yeet")
        client._path_modules[path.absolute()] = mock_module

        with pytest.raises(tanjun.FailedModuleUnload) as exc_info:
            client.unload_modules(path)

        assert exc_info.value.__cause__ is mock_exception
        assert client._path_modules[path.absolute()] is mock_module

    def test_unload_modules_with_python_module_path(self):
        client = tanjun.Client(mock.AsyncMock())
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True))

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            other_loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True)),
            loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False)),
            no=object(),
            _priv_loader=priv_loader,
            __all__=None,
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            result = client.load_modules("okokok.no").unload_modules("okokok.no")

            import_module.assert_called_once_with("okokok.no")

        assert result is client
        mock_module.other_loader.unload.assert_called_once_with(client)
        mock_module.loader.unload.assert_called_once_with(client)
        priv_loader.unload.assert_not_called()
        assert "okokok.no" not in client._modules

    def test_unload_modules_with_python_module_path_respects_all(self):
        client = tanjun.Client(mock.AsyncMock())
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True))

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False)),
            no=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True)),
            _priv_loader=priv_loader,
            another_loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True)),
            __all__=["loader", "_priv_loader", "another_loader", "missing"],
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            client.load_modules("okokok.no.u")

            import_module.assert_called_once_with("okokok.no.u")

        client.unload_modules("okokok.no.u")

        mock_module.loader.unload.assert_called_once_with(client)
        mock_module.other_loader.assert_not_called()
        priv_loader.unload.assert_called_once_with(client)
        mock_module.another_loader.unload.assert_called_once_with(client)
        assert "okokok.no.u" not in client._modules

    def test_unload_modules_with_python_module_path_when_not_loaded(self):
        client = tanjun.Client(mock.AsyncMock())

        with pytest.raises(tanjun.ModuleStateConflict):
            client.unload_modules("gay.cat")

        assert "gay.cat" not in client._modules

    def test_unload_modules_with_python_module_path_when_no_unloaders_found_and_all(self):
        client = tanjun.Client(mock.AsyncMock())
        other_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=True))

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False)),
            no=object(),
            other_loader=other_loader,
            __all__=["loader", "missing"],
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            client.load_modules("senpai.uwu")

            with pytest.raises(tanjun.ModuleMissingLoaders):
                client.unload_modules("senpai.uwu")

            import_module.assert_called_once_with("senpai.uwu")
            other_loader.assert_not_called()

        mock_module.loader.unload.assert_called_once_with(client)
        assert "senpai.uwu" in client._modules

    def test_unload_modules_with_python_module_path_when_no_unloaders_found(self):
        client = tanjun.Client(mock.AsyncMock())

        mock_module = mock.Mock(
            object=123,
            foo="ok",
            loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False)),
            no=object(),
        )

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            client.load_modules("okokok.nok")

            with pytest.raises(tanjun.ModuleMissingLoaders):
                client.unload_modules("okokok.nok")

            import_module.assert_called_once_with("okokok.nok")

        mock_module.loader.unload.assert_called_once_with(client)
        assert "okokok.nok" in client._modules

    def test_unload_modules_with_python_module_path_when_unloader_raises(self):
        client = tanjun.Client(mock.AsyncMock())
        mock_exception = TypeError("Big shot")
        mock_module = mock.Mock(
            foo=5686544536876,
            bar=object(),
            loader=mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(side_effect=mock_exception)),
        )
        client._modules["ea s"] = mock_module

        with pytest.raises(tanjun.FailedModuleUnload) as exc_info:
            client.unload_modules("ea s")

        assert exc_info.value.__cause__ is mock_exception
        assert client._modules["ea s"] is mock_module
        assert "ea s" in client._modules

    def test__reload_modules_with_python_module_path(self):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False))
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(unload=False)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        new_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=False)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("waifus")

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_not_called()
        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("waifus")
            module = next(generator)()
            try:
                generator.send(module)

            except StopIteration:
                pass

            else:
                pytest.fail("Expected StopIteration")

            reload.assert_called_once_with(old_module)

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_called_once_with(client)
        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_called_once_with(client)
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_called_once_with(client)
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._modules["waifus"] is new_module

    def test__reload_modules_with_python_module_path_when_no_unloaders_found(self):
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            load=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True), has_unload=False),
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
        )
        new_module = mock.Mock(ok=123, loader=mock.Mock(tanjun.abc.ClientLoader))
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("waifus")

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("waifus")
            with pytest.raises(tanjun.ModuleMissingLoaders):
                next(generator)

            reload.assert_not_called()

        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        assert client._modules["waifus"] is old_module

    def test__reload_modules_with_python_module_path_when_no_loaders_found_in_new_module(self):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        new_module = mock.Mock(
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("yuri.waifus")

        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("yuri.waifus")
            module = next(generator)()

            with pytest.raises(tanjun.ModuleMissingLoaders):
                generator.send(module)

            reload.assert_called_once_with(old_module)

        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._modules["yuri.waifus"] is old_module

    def test__reload_modules_with_python_module_path_when_all(self):
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            _priv_loader=old_priv_loader,
            __all__=["loader", "other_loader", "ok", "_priv_loader"],
        )
        new_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=priv_loader,
            __all__=["loader", "_priv_loader"],
        )
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("waifus")

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_called_once_with(client)
        old_priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("waifus")
            module = next(generator)()
            try:
                generator.send(module)

            except StopIteration:
                pass

            else:
                pytest.fail("Expected StopIteration")

            reload.assert_called_once_with(old_module)

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_called_once_with(client)
        old_priv_loader.unload.assert_called_once_with(client)
        new_module.loader.load.assert_called_once_with(client)
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_called_once_with(client)
        priv_loader.unload.assert_not_called()
        assert client._modules["waifus"] is new_module

    def test__reload_modules_with_python_module_path_when_all_and_no_unloaders_found(self):
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, has_unload=False),
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            __all__=["naye", "loader", "ok"],
        )
        new_module = mock.Mock(loader=mock.Mock(tanjun.abc.ClientLoader, has_unload=False), foo=object())
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("waifus")

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("waifus")

            with pytest.raises(tanjun.ModuleMissingLoaders):
                next(generator)

            reload.assert_not_called()

        priv_loader.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        assert client._modules["waifus"] is old_module

    def test__reload_modules_with_python_module_path_when_all_and_no_loaders_found_in_new_module(self):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
            __all__=["loader", "ok", "naye"],
        )
        new_module = mock.Mock(
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
            loader=mock.Mock(tanjun.abc.ClientLoader, has_load=True),
            __all__=["ok", "naye"],
        )
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("yuri.waifus")

        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("yuri.waifus")
            module = next(generator)()

            with pytest.raises(tanjun.ModuleMissingLoaders):
                generator.send(module)

            reload.assert_called_once_with(old_module)

        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        assert client._modules["yuri.waifus"] is old_module

    def test__reload_modules_with_python_module_path_and_not_loaded(self):
        client = tanjun.Client(mock.AsyncMock())
        generator = client._reload_module("aya.gay.no")

        with pytest.raises(tanjun.ModuleStateConflict):
            next(generator)

        assert "aya.gay.no" not in client._modules

    def test__reload_modules_with_python_module_path_rolls_back_when_new_module_loader_raises(self):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False))
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(unload=False)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        mock_exception = KeyError("Aaaaaaaa")
        new_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=False, side_effect=mock_exception)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())

        with mock.patch.object(importlib, "import_module", return_value=old_module):
            client.load_modules("waifus")

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_not_called()
        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_not_called()
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()

        with mock.patch.object(importlib, "reload", return_value=new_module) as reload:
            generator = client._reload_module("waifus")
            module = next(generator)()

            with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
                generator.send(module)

            assert exc_info.value.__cause__ is mock_exception
            reload.assert_called_once_with(old_module)

        old_module.other_loader.load.assert_has_calls([mock.call(client), mock.call(client)])
        old_module.other_loader.unload.assert_called_once_with(client)
        old_module.loader.load.assert_has_calls([mock.call(client), mock.call(client)])
        old_module.loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        new_module.loader.load.assert_called_once_with(client)
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._modules["waifus"] is old_module

    def test__reload_modules_with_system_path(self, file: typing.IO[str]):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(unload=False)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                loader = mock.Mock(tanjun.abc.ClientLoader, has_load=False, load=mock.Mock(return_value=False))
                ok = 123
                naye = object()
                other_loader = mock.Mock(tanjun.abc.ClientLoader, has_load=True)
                _priv_loader = mock.Mock(tanjun.abc.ClientLoader)
                """
            )
        )
        file.flush()

        client._path_modules[path] = old_module

        generator = client._reload_module(path)
        module = next(generator)()
        try:
            generator.send(module)

        except StopIteration:
            pass

        else:
            pytest.fail("Expected StopIteration")

        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_called_once_with(client)
        old_module.loader.load.assert_not_called()
        old_module.loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        client._path_modules[path].loader.load.assert_called_once_with(client)
        client._path_modules[path].loader.unload.assert_not_called()
        client._path_modules[path].other_loader.load.assert_called_once_with(client)
        client._path_modules[path].other_loader.unload.assert_not_called()
        client._path_modules[path]._priv_loader.load.assert_not_called()
        client._path_modules[path]._priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is not old_module

    def test__reload_modules_with_system_path_when_no_unloaders_found(self, file: typing.IO[str]):
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            load=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(return_value=True), has_unload=False),
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                loader = mock.Mock(
                    tanjun.abc.ClientLoader,
                    load=mock.Mock(side_effect=RuntimeError("This shouldn't be called")),
                )
                """
            )
        )
        file.flush()
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        generator = client._reload_module(path)

        with pytest.raises(tanjun.ModuleMissingLoaders):
            next(generator)

        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is old_module

    def test__reload_modules_with_system_path_when_no_loaders_found_in_new_module(self, file: typing.IO[str]):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                ok = 123
                naye = object()
                loader = mock.Mock(tanjun.abc.ClientLoader, has_load=False)
                _priv_loader = mock.Mock(tanjun.abc.ClientLoader)
                """
            )
        )
        file.flush()
        generator = client._reload_module(path)
        module = next(generator)()

        with pytest.raises(tanjun.ModuleMissingLoaders):
            generator.send(module)

        old_module.loader.load.assert_not_called()
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is old_module

    def test__reload_modules_with_system_path_when_all(self, file: typing.IO[str]):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            _priv_loader=old_priv_loader,
            __all__=["loader", "other_loader", "ok", "_priv_loader"],
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                loader = mock.Mock(tanjun.abc.ClientLoader)
                ok = 123
                naye = object()
                other_loader = mock.Mock(tanjun.abc.ClientLoader)
                _priv_loader = mock.Mock(tanjun.abc.ClientLoader)
                __all__ = ["loader", "_priv_loader"]
                """
            )
        )
        file.flush()

        generator = client._reload_module(path)
        module = next(generator)()
        try:
            generator.send(module)

        except StopIteration:
            pass

        else:
            pytest.fail("Expected StopIteration")

        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_called_once_with(client)
        new_module = client._path_modules[path]
        new_module.loader.load.assert_called_once_with(client)
        new_module.loader.unload.assert_not_called()
        new_module.other_loader.load.assert_not_called()
        new_module.other_loader.unload.assert_not_called()
        new_module._priv_loader.load.assert_called_once_with(client)
        new_module._priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is not old_module

    def test__reload_modules_with_system_path_when_all_and_no_unloaders_found(self, file: typing.IO[str]):
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, has_unload=False),
            ok=123,
            naye=object(),
            _priv_loader=priv_loader,
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            __all__=["naye", "loader", "ok"],
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                loader = mock.Mock(
                    tanjun.abc.ClientLoader,
                    has_unload=False,
                    unload=mock.Mock(side_effect=RuntimeError("This shouldn't ever be called"))
                )
                foo = object()
                """
            )
        )
        file.flush()
        generator = client._reload_module(path)

        with pytest.raises(tanjun.ModuleMissingLoaders):
            next(generator)

        priv_loader.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        assert client._path_modules[path] is old_module

    def test__reload_modules_with_system_path_when_all_and_no_loaders_found_in_new_module(self, file: typing.IO[str]):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
            __all__=["loader", "ok", "naye"],
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                ok = 123
                naye = object()
                _priv_loader = mock.Mock(
                    tanjun.abc.ClientLoader,
                    has_load=True,
                    load=mock.Mock(side_effect=RuntimeError("This shouldn't ever be called"))
                )
                loader = mock.Mock(
                    tanjun.abc.ClientLoader,
                    has_load=True,
                    load=mock.Mock(side_effect=RuntimeError("This shouldn't ever be called"))
                )
                __all__ = ["ok", "naye"]
                """
            )
        )
        file.flush()
        generator = client._reload_module(path)
        module = next(generator)()

        with pytest.raises(tanjun.ModuleMissingLoaders):
            generator.send(module)

        old_module.loader.load.assert_not_called()
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is old_module

    def test__reload_modules_with_system_path_and_not_loaded(self):
        client = tanjun.Client(mock.AsyncMock())
        random_path = pathlib.Path(base64.urlsafe_b64encode(random.randbytes(64)).decode())
        generator = client._reload_module(random_path)

        with pytest.raises(tanjun.ModuleStateConflict):
            next(generator)

        assert random_path not in client._path_modules

    def test__reload_modules_with_system_path_for_unknown_path(self):
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
        )
        client = tanjun.Client(mock.AsyncMock())
        random_path = pathlib.Path(base64.urlsafe_b64encode(random.randbytes(64)).decode())
        client._path_modules[random_path.absolute()] = old_module
        generator = client._reload_module(random_path.absolute())
        next_ = next(generator)

        with pytest.raises(ModuleNotFoundError):
            next_()

        old_module.loader.load.assert_not_called()
        old_module.loader.unload.assert_not_called()
        old_module.other_loader.load.assert_not_called()
        old_module.other_loader.unload.assert_not_called()
        assert random_path not in client._path_modules

    def test__reload_modules_with_system_path_rolls_back_when_new_module_loader_raises(self, file: typing.IO[str]):
        old_priv_loader = mock.Mock(tanjun.abc.ClientLoader)
        priv_loader = mock.Mock(tanjun.abc.ClientLoader, unload=mock.Mock(return_value=False))
        old_module = mock.Mock(
            loader=mock.Mock(tanjun.abc.ClientLoader, load=mock.Mock(unload=False)),
            ok=123,
            naye=object(),
            other_loader=mock.Mock(tanjun.abc.ClientLoader),
            _priv_loader=old_priv_loader,
        )
        client = tanjun.Client(mock.AsyncMock())
        path = pathlib.Path(file.name)
        client._path_modules[path] = old_module
        file.write(
            textwrap.dedent(
                """
                from unittest import mock

                import tanjun

                loader = mock.Mock(
                    tanjun.abc.ClientLoader,
                    load=mock.Mock(return_value=False, side_effect=KeyError("Aaaaaaaaaaaaa"))
                )
                ok = 123
                naye = object()
                other_loader = mock.Mock(tanjun.abc.ClientLoader)
                _priv_loader = mock.Mock(tanjun.abc.ClientLoader)
                """
            )
        )
        file.flush()
        generator = client._reload_module(path)
        module = next(generator)()

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            generator.send(module)

        assert isinstance(exc_info.value.__cause__, KeyError)
        assert exc_info.value.__cause__.args == ("Aaaaaaaaaaaaa",)

        old_module.other_loader.load.assert_called_once_with(client)
        old_module.other_loader.unload.assert_called_once_with(client)
        old_module.loader.load.assert_called_once_with(client)
        old_module.loader.unload.assert_called_once_with(client)
        old_priv_loader.load.assert_not_called()
        old_priv_loader.unload.assert_not_called()
        priv_loader.load.assert_not_called()
        priv_loader.unload.assert_not_called()
        assert client._path_modules[path] is old_module

    def test_reload_modules(self):
        mock_path = mock.Mock(pathlib.Path)
        mock_gen_1 = mock.Mock(__next__=mock.Mock())
        mock_gen_1.send.side_effect = StopIteration
        mock_gen_2 = mock.Mock(__next__=mock.Mock())
        mock_gen_2.send.side_effect = StopIteration
        mock__reload_module = mock.Mock(side_effect=[mock_gen_1, mock_gen_2])

        class StubClient(tanjun.Client):
            _reload_module = mock__reload_module

        client = StubClient(mock.AsyncMock())

        result = client.reload_modules(mock_path, "ok.no.u")

        assert result is client
        mock__reload_module.assert_has_calls([mock.call(mock_path.absolute.return_value), mock.call("ok.no.u")])
        mock_path.absolute.assert_called_once_with()
        mock_gen_1.__next__.assert_called_once_with()
        mock_gen_1.__next__.return_value.assert_called_once_with()
        mock_gen_1.send.assert_called_once_with(mock_gen_1.__next__.return_value.return_value)
        mock_gen_2.__next__.assert_called_once_with()
        mock_gen_2.__next__.return_value.assert_called_once_with()
        mock_gen_2.send.assert_called_once_with(mock_gen_2.__next__.return_value.return_value)

    def test_reload_modules_when_module_loader_raises(self):
        mock_exception = TypeError("FOO")
        mock_gen = mock.Mock(__next__=mock.Mock())
        mock_gen.__next__.return_value.side_effect = mock_exception
        mock__reload_module = mock.Mock(return_value=mock_gen)

        class StubClient(tanjun.Client):
            _reload_module = mock__reload_module

        client = StubClient(mock.AsyncMock())

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            client.reload_modules("ok.no.u")

        assert exc_info.value.__cause__ is mock_exception

        mock__reload_module.assert_called_once_with("ok.no.u")
        mock_gen.__next__.assert_called_once_with()
        mock_gen.__next__.return_value.assert_called_once_with()
        mock_gen.send.assert_not_called()

    @mock.patch.object(asyncio, "get_running_loop")
    @pytest.mark.asyncio()
    async def test_reload_modules_async(self, get_running_loop: mock.Mock):
        mock_executor_result_1 = mock.Mock()
        mock_executor_result_2 = mock.Mock()
        mock_executor_result_3 = mock.Mock()
        get_running_loop.return_value.run_in_executor = mock.AsyncMock(
            side_effect=[mock_executor_result_1, mock_executor_result_2, mock_executor_result_3]
        )
        mock_path = mock.Mock(pathlib.Path)
        mock_gen_1 = mock.Mock(__next__=mock.Mock())
        mock_gen_1.send.side_effect = StopIteration
        mock_gen_2 = mock.Mock(__next__=mock.Mock())
        mock_gen_2.send.side_effect = StopIteration
        mock__reload_module = mock.Mock(side_effect=[mock_gen_1, mock_gen_2])

        class StubClient(tanjun.Client):
            _reload_module = mock__reload_module

        client = StubClient(mock.AsyncMock())

        result = await client.reload_modules_async(mock_path, "ok.no.u")

        assert result is None
        mock__reload_module.assert_has_calls([mock.call(mock_executor_result_1), mock.call("ok.no.u")])
        mock_gen_1.__next__.assert_called_once_with()
        mock_gen_1.send.assert_called_once_with(mock_executor_result_2)
        mock_gen_2.__next__.assert_called_once_with()
        mock_gen_2.send.assert_called_once_with(mock_executor_result_3)
        get_running_loop.assert_called_once_with()
        get_running_loop.return_value.run_in_executor.assert_has_calls(
            [
                mock.call(None, mock_path.absolute),
                mock.call(None, mock_gen_1.__next__.return_value),
                mock.call(None, mock_gen_2.__next__.return_value),
            ]
        )

    @mock.patch.object(asyncio, "get_running_loop")
    @pytest.mark.asyncio()
    async def test_reload_modules_async_when_module_loader_raises(self, get_running_loop: mock.Mock):
        mock_exception = RuntimeError("eeeee")
        get_running_loop.return_value.run_in_executor = mock.AsyncMock(side_effect=mock_exception)
        mock_gen = mock.Mock(__next__=mock.Mock())
        mock__reload_module = mock.Mock(return_value=mock_gen)

        class StubClient(tanjun.Client):
            _reload_module = mock__reload_module

        client = StubClient(mock.AsyncMock())

        with pytest.raises(tanjun.FailedModuleLoad) as exc_info:
            await client.reload_modules_async("ok.no.u")

        assert exc_info.value.__cause__ is mock_exception

        mock__reload_module.assert_called_once_with("ok.no.u")
        mock_gen.__next__.assert_called_once_with()
        mock_gen.send.assert_not_called()
        get_running_loop.assert_called_once_with()
        get_running_loop.return_value.run_in_executor.assert_called_once_with(None, mock_gen.__next__.return_value)

    # Message create event

    @pytest.fixture()
    def command_dispatch_client(self) -> tanjun.Client:
        class StubClient(tanjun.Client):
            check = mock.AsyncMock()
            dispatch_client_callback = mock.AsyncMock()

        return (
            StubClient(mock.AsyncMock())
            .set_hooks(mock.Mock())
            .set_message_hooks(mock.Mock())
            .set_slash_hooks(mock.Mock())
            .set_prefix_getter(mock.AsyncMock())
        )

    @pytest.mark.asyncio()
    async def test_on_message_create_event(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_component(mock_component_1).add_component(mock_component_2).add_prefix(
            "!"
        ).set_message_ctx_maker(ctx_maker)
        mock_component_1.execute_message.return_value = True
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_no_message_content(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock()
        command_dispatch_client.set_message_ctx_maker(ctx_maker)
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_component(mock_component_1).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)

        await command_dispatch_client.on_message_create_event(mock.Mock(message=mock.Mock(content=None)))

        ctx_maker.assert_not_called()
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_prefix_not_found(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="42"))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_prefix("gay").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        mock_event = mock.Mock(message=mock.Mock(content="eye"))
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_custom_prefix_getter_not_found(
        self, command_dispatch_client: tanjun.Client
    ):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="42"))
        prefix_getter = mock.AsyncMock(return_value=["aye", "naye"])
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_prefix("gay").set_message_ctx_maker(ctx_maker).set_prefix_getter(
            prefix_getter
        ).add_component(mock_component_1).add_component(mock_component_2)
        mock_event = mock.Mock(message=mock.Mock(content="eye"))
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_only_message_hooks(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = True
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).set_hooks(None).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.message_hooks}
        )
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_only_generic_hooks(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = True
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).set_message_hooks(None).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks}
        )
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_no_hooks(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = True
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).set_hooks(None).set_message_hooks(
            None
        ).add_component(mock_component_1).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(ctx_maker.return_value, hooks=None)
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_checks_raise_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.side_effect = tanjun.CommandError("eee")
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_awaited_once_with("eee")
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_checks_raise_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.side_effect = tanjun.HaltExecution()
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_awaited_once_with(
            tanjun.ClientCallbackNames.MESSAGE_COMMAND_NOT_FOUND, ctx_maker.return_value
        )

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_checks_returns_false(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = False
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_not_called()
        mock_component_2.execute_message.assert_not_called()
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_awaited_once_with(
            tanjun.ClientCallbackNames.MESSAGE_COMMAND_NOT_FOUND, ctx_maker.return_value
        )

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_component_raises_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = False
        mock_component_2.execute_message.side_effect = tanjun.CommandError("eeea")
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        mock_component_2.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        ctx_maker.return_value.respond.assert_awaited_once_with("eeea")
        command_dispatch_client.dispatch_client_callback.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_component_raises_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = False
        mock_component_2.execute_message.side_effect = tanjun.HaltExecution
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        mock_component_2.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_awaited_once_with(
            tanjun.ClientCallbackNames.MESSAGE_COMMAND_NOT_FOUND, ctx_maker.return_value
        )

    @pytest.mark.asyncio()
    async def test_on_message_create_event_when_not_found(self, command_dispatch_client: tanjun.Client):
        ctx_maker = mock.Mock(return_value=mock.Mock(content="!  42", respond=mock.AsyncMock()))
        ctx_maker.return_value.set_content.return_value = ctx_maker.return_value
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_1.execute_message.return_value = False
        mock_component_2.execute_message.return_value = False
        command_dispatch_client.add_prefix("!").set_message_ctx_maker(ctx_maker).add_component(
            mock_component_1
        ).add_component(mock_component_2)
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        assert isinstance(command_dispatch_client.dispatch_client_callback, mock.AsyncMock)
        command_dispatch_client.check.return_value = True
        mock_event = mock.Mock(message=mock.Mock(content="eye"))

        await command_dispatch_client.on_message_create_event(mock_event)

        ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            content="eye",
            message=mock_event.message,
        )
        ctx_maker.return_value.set_content.assert_called_once_with("42")
        ctx_maker.return_value.set_triggering_prefix.assert_called_once_with("!")
        command_dispatch_client.check.assert_awaited_once_with(ctx_maker.return_value)
        mock_component_1.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        mock_component_2.execute_message.assert_awaited_once_with(
            ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.message_hooks}
        )
        ctx_maker.return_value.respond.assert_not_called()
        command_dispatch_client.dispatch_client_callback.assert_awaited_once_with(
            tanjun.ClientCallbackNames.MESSAGE_COMMAND_NOT_FOUND, ctx_maker.return_value
        )

    # Interaction create event

    @pytest.mark.asyncio()
    async def test__on_slash_not_found(self):
        dispatch_client_callback_ = mock.AsyncMock()

        class StubClient(tanjun.Client):
            dispatch_client_callback = dispatch_client_callback_

        client = StubClient(mock.AsyncMock).set_interaction_not_found("gay")
        ctx = mock.AsyncMock(has_responded=False)

        await client._on_slash_not_found(ctx)

        ctx.create_initial_response.assert_awaited_once_with("gay")
        dispatch_client_callback_.assert_awaited_once_with(tanjun.ClientCallbackNames.SLASH_COMMAND_NOT_FOUND, ctx)

    @pytest.mark.asyncio()
    async def test__on_slash_not_found_when_already_responded(self):
        dispatch_client_callback_ = mock.AsyncMock()

        class StubClient(tanjun.Client):
            dispatch_client_callback = dispatch_client_callback_

        client = StubClient(mock.AsyncMock).set_interaction_not_found("gay")
        ctx = mock.AsyncMock(has_responded=True)

        await client._on_slash_not_found(ctx)

        ctx.create_initial_response.assert_not_called()
        dispatch_client_callback_.assert_awaited_once_with(tanjun.ClientCallbackNames.SLASH_COMMAND_NOT_FOUND, ctx)

    @pytest.mark.asyncio()
    async def test__on_slash_not_found_when_not_found_messages_disabled(self):
        dispatch_client_callback_ = mock.AsyncMock()

        class StubClient(tanjun.Client):
            dispatch_client_callback = dispatch_client_callback_

        client = StubClient(mock.AsyncMock).set_interaction_not_found(None)
        ctx = mock.AsyncMock(has_responded=False)

        await client._on_slash_not_found(ctx)

        ctx.create_initial_response.assert_not_called()
        dispatch_client_callback_.assert_awaited_once_with(tanjun.ClientCallbackNames.SLASH_COMMAND_NOT_FOUND, ctx)

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_future = mock.AsyncMock()
        mock_component_2.execute_interaction.return_value = mock_future()
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_future.assert_awaited_once()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.parametrize("interaction_type", [hikari.MessageInteraction])
    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_not_message_interaction(
        self, command_dispatch_client: tanjun.Client, interaction_type: type[hikari.PartialInteraction]
    ):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).add_component(mock_component_1).add_component(
            mock_component_2
        )
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)

        await command_dispatch_client.on_interaction_create_event(mock.Mock(interaction=mock.Mock(interaction_type)))

        mock_ctx_maker.assert_not_called()
        mock_component_1.execute_interaction.assert_not_called()
        mock_component_2.execute_interaction.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_ephemeral_default(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            None
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(
            mock_component_2
        ).set_ephemeral_default(
            True
        )
        mock_component_1.execute_interaction.return_value = None
        mock_future = mock.AsyncMock()
        mock_component_2.execute_interaction.return_value = mock_future()
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=True,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_future.assert_awaited_once()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_not_auto_deferring(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(None).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.return_value = None
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_not_called()
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_awaited_once_with()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_no_hooks(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).set_slash_hooks(None).set_hooks(None).add_component(mock_component_1).add_component(
            mock_component_2
        )
        mock_component_1.execute_interaction.return_value = None
        mock_future = mock.AsyncMock()
        mock_component_2.execute_interaction.return_value = mock_future()
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(mock_ctx_maker.return_value, hooks=None)
        mock_component_2.execute_interaction.assert_awaited_once_with(mock_ctx_maker.return_value, hooks=None)
        mock_future.assert_awaited_once()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_only_slash_hooks(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).set_hooks(None).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_future = mock.AsyncMock()
        mock_component_2.execute_interaction.return_value = mock_future()
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.slash_hooks}
        )
        mock_future.assert_awaited_once()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_only_generic_hooks(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).set_slash_hooks(None).add_component(mock_component_1).add_component(
            mock_component_2
        )
        mock_component_1.execute_interaction.return_value = None
        mock_future = mock.AsyncMock()
        mock_component_2.execute_interaction.return_value = mock_future()
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks}
        )
        mock_future.assert_awaited_once()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_not_found(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.return_value = None
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_awaited_once_with()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_checks_raise_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.return_value = None
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.side_effect = tanjun.CommandError("3903939")

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_not_called()
        mock_component_2.execute_interaction.assert_not_called()
        mock_ctx_maker.return_value.respond.assert_awaited_once_with("3903939")
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_checks_raise_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.return_value = None
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.side_effect = tanjun.HaltExecution()

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_not_called()
        mock_component_2.execute_interaction.assert_not_called()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_awaited_once_with()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_component_raises_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.side_effect = tanjun.CommandError("123321")
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_ctx_maker.return_value.respond.assert_awaited_once_with("123321")
        mock_ctx_maker.return_value.mark_not_found.assert_not_called()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_component_raises_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.side_effect = tanjun.HaltExecution
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = True

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_component_2.execute_interaction.assert_awaited_once_with(
            mock_ctx_maker.return_value, hooks={command_dispatch_client.hooks, command_dispatch_client.slash_hooks}
        )
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_awaited_once_with()

    @pytest.mark.asyncio()
    async def test_on_interaction_create_event_when_checks_fail(self, command_dispatch_client: tanjun.Client):
        mock_ctx_maker = mock.Mock(return_value=mock.Mock(respond=mock.AsyncMock(), mark_not_found=mock.AsyncMock()))
        mock_component_1 = mock.AsyncMock(bind_client=mock.Mock())
        mock_component_2 = mock.AsyncMock(bind_client=mock.Mock())
        command_dispatch_client.set_slash_ctx_maker(mock_ctx_maker).set_interaction_not_found(
            "Interaction not found"
        ).set_auto_defer_after(2.2).add_component(mock_component_1).add_component(mock_component_2)
        mock_component_1.execute_interaction.return_value = None
        mock_component_2.execute_interaction.return_value = None
        mock_event = mock.Mock(interaction=mock.Mock(hikari.CommandInteraction))
        assert isinstance(command_dispatch_client.check, mock.AsyncMock)
        command_dispatch_client.check.return_value = False

        await command_dispatch_client.on_interaction_create_event(mock_event)

        mock_ctx_maker.assert_called_once_with(
            client=command_dispatch_client,
            injection_client=command_dispatch_client,
            interaction=mock_event.interaction,
            on_not_found=command_dispatch_client._on_slash_not_found,
            default_to_ephemeral=False,
        )
        mock_ctx_maker.return_value.start_defer_timer.assert_called_once_with(2.2)
        mock_component_1.execute_interaction.assert_not_called()
        mock_component_2.execute_interaction.assert_not_called()
        mock_ctx_maker.return_value.respond.assert_not_called()
        mock_ctx_maker.return_value.mark_not_found.assert_awaited_once_with()

    # Note, these will likely need to be more integrationy than the above tests to ensure there's no deadlocking
    # behaviour around ctx and its owned future.
    # Interaction create REST request
    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_ephemeral_default(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_not_auto_deferring(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_no_hooks(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_only_slash_hooks(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_only_generic_hooks(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_not_found(self, command_dispatch_client: tanjun.Client):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_checks_raise_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_checks_raise_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_component_raises_command_error(
        self, command_dispatch_client: tanjun.Client
    ):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_component_raises_halt_execution(
        self, command_dispatch_client: tanjun.Client
    ):
        ...

    @pytest.mark.skip(reason="TODO")
    @pytest.mark.asyncio()
    async def test_on_interaction_create_request_when_checks_fail(self, command_dispatch_client: tanjun.Client):
        ...
