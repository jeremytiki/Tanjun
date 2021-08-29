# -*- coding: utf-8 -*-
# cython: language_level=3
# BSD 3-Clause License
#
# Copyright (c) 2020-2021, Faster Speeding
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
# This leads to too many false-positives around mocks.

import base64
import importlib
import pathlib
import random
import tempfile
import textwrap
from unittest import mock

import pytest

import tanjun


class TestClient:

    # def from_gateway_bot(self):
    #     mock_builder = mock.Mock()
    #     mock_builder.set_human_only.return_value = mock_builder
    #     mock_builder.set_hikari_trait_injectors.return_value = mock_builder
    #     mock_bot = mock.Mock()

    #     with mock.patch.object(tanjun.Client, "__init__", return_value=mock_builder) as __init__:
    #         result = tanjun.Client.from_gateway_bot(
    #             mock_bot, event_managed=False, mention_prefix=True, set_global_commands=123321
    #         )

    #         assert result is mock_builder.set_hikari_trait_injectors.return_value
    #         mock_builder.set_hikari_trait_injector.assert_called_once_with(mock_bot)
    #         mock_builder.set_human_only.assert_called_once_with()
    #         __init__.assert_called_once_with(
    #             rest=mock_bot.rest,
    #             cache=mock_bot.cache,
    #             events=mock_bot.event_manager,
    #             shards=mock_bot,
    #             event_managed=False,
    #             mention_prefix=True,
    #             set_global_commands=123321,
    #         )

    # def test_set_hikari_trait_injectors(self):
    #     class MockClient(tanjun.Client):
    #         __slots__ = ()
    #         __init__ = mock.Mock()
    #         set_hikari_trait_injectors = mock.Mock()

    #     MockClient.set_hikari_trait_injectors.return_value = mock_builder
    #     mock_bot = mock.Mock()

    #     result = MockClient.from_rest_bot(
    #         mock_bot,set_global_commands=123321
    #     )

    #     assert result is mock_builder
    #     MockClient.set_hikari_trait_injectors.assert_called_once_with(mock_bot)
    #     MockClient.__init__.assert_called_once_with(
    #         rest=mock_bot.rest,
    #         server=mock_bot.injection_server,
    #         set_global_commands=123321,
    #     )

    @pytest.mark.asyncio()
    async def test_async_context_manager(self) -> None:
        class StudClient(tanjun.Client):
            __slots__ = ()
            close = mock.AsyncMock()
            open = mock.AsyncMock()

        client = StudClient(mock.Mock())
        async with client:
            client.open.assert_called_once_with()
            client.close.assert_not_called()

        client.open.assert_called_once_with()
        client.close.assert_called_once_with()

    @pytest.mark.skip(reason="not implemented")
    def test___repr__(self) -> None:
        raise NotImplementedError

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

    @pytest.mark.skip(reason="not implemented")
    def test_checks_property(self) -> None:
        raise NotImplementedError

    @pytest.mark.skip(reason="not implemented")
    def test_components_property(self) -> None:
        raise NotImplementedError

    def test_events_property(self) -> None:
        mock_events = mock.Mock()
        client = tanjun.Client(mock.Mock(), events=mock_events)

        assert client.events is mock_events

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

        assert client.is_alive is client._is_alive

    def test_message_hooks_property(self) -> None:
        mock_hooks = mock.Mock()
        client = tanjun.Client(mock.Mock()).set_message_hooks(mock_hooks)

        assert client.message_hooks is mock_hooks

    @pytest.mark.skip(reason="not implemented")
    def test_metadata_property(self) -> None:
        raise NotImplementedError

    @pytest.mark.skip(reason="not implemented")
    def test_prefix_getter_property(self) -> None:
        raise NotImplementedError

    def test_prefixes_property(self) -> None:
        client = tanjun.Client(mock.Mock()).add_prefix("a").add_prefix("b")

        assert client.prefixes == {"a", "b"}

    def test_rest_property(self) -> None:
        mock_rest = mock.Mock()
        client = tanjun.Client(mock_rest)

        assert client.rest is mock_rest

    def test_server_property(self) -> None:
        mock_server = mock.Mock()
        client = tanjun.Client(mock.Mock, server=mock_server)

        assert client.server is mock_server

    def test_shards_property(self) -> None:
        mock_shards = mock.Mock()
        client = tanjun.Client(mock.Mock(), shards=mock_shards)

        assert client.shards is mock_shards

    def test_load_modules_with_system_path(self):
        class MockClient(tanjun.Client):
            add_component = mock.Mock()

            add_client_callback = mock.Mock()

        client = MockClient(mock.AsyncMock())

        # A try, finally is used to delete the file rather than relying on delete=True behaviour
        # as on Windows the file cannot be accessed by other processes if delete is True.
        file = tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False)
        path = pathlib.Path(file.name)
        try:
            with file:
                file.write(
                    textwrap.dedent(
                        """
                        import tanjun

                        foo = 123
                        bar = object()

                        @tanjun.as_loader
                        def load_module(client: tanjun.abc.Client) -> None:
                            assert isinstance(client, tanjun.Client)
                            client.add_component(123)
                            client.add_client_callback(4312)
                    """
                    )
                )
                file.flush()

            client.load_modules(path)

            client.add_component.assert_called_once_with(123)
            client.add_client_callback.assert_called_once_with(4312)

        finally:
            path.unlink(missing_ok=False)

    def test_load_modules_with_system_path_for_unknown_path(self):
        class MockClient(tanjun.Client):
            add_component = mock.Mock()
            add_client_callback = mock.Mock()

        client = MockClient(mock.AsyncMock())
        random_path = pathlib.Path(base64.urlsafe_b64encode(random.randbytes(64)).decode())

        with pytest.raises(RuntimeError):
            client.load_modules(random_path)

    def test_load_modules_with_python_module_path(self):
        client = tanjun.Client(mock.AsyncMock())

        mock_module = mock.Mock(object=123, foo="ok", loader=mock.Mock(tanjun.clients._LoadableDescriptor), no=object())

        with mock.patch.object(importlib, "import_module", return_value=mock_module) as import_module:
            client.load_modules("okokok.no.u")

            import_module.assert_called_once_with("okokok.no.u")

        mock_module.loader.assert_called_once_with(client)
