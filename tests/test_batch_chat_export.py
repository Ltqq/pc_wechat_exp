# -*- coding: utf-8 -*-
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from main import _load_chat_targets_file, _resolve_chat_targets


def _chat(username, name):
    return {
        "username": username,
        "display_name": name,
        "is_group": username.endswith("@chatroom"),
        "msg_count": 0,
    }


def test_load_chat_targets_file_ignores_blank_comments_and_duplicates(tmp_path):
    p = tmp_path / "groups.txt"
    p.write_text(
        "\ufeff# 工作群\n研发群\n\n产品群\n研发群\nroom@chatroom\n",
        encoding="utf-8",
    )
    assert _load_chat_targets_file(str(p)) == [
        "研发群", "产品群", "room@chatroom"
    ]


def test_resolve_chat_targets_matches_id_and_display_name():
    chats = [
        _chat("a@chatroom", "研发群"),
        _chat("b@chatroom", "产品群"),
        _chat("wxid_user", "张三"),
    ]
    selected, missing, ambiguous = _resolve_chat_targets(
        chats, ["研发群", "b@chatroom"]
    )
    assert [x["username"] for x in selected] == ["a@chatroom", "b@chatroom"]
    assert missing == []
    assert ambiguous == []


def test_resolve_chat_targets_groups_only_filters_private_chat():
    chats = [
        _chat("a@chatroom", "研发群"),
        _chat("wxid_user", "张三"),
    ]
    selected, missing, ambiguous = _resolve_chat_targets(
        chats, ["研发群", "张三"], groups_only=True
    )
    assert [x["username"] for x in selected] == ["a@chatroom"]
    assert missing == ["张三"]
    assert ambiguous == []


def test_resolve_chat_targets_duplicate_names_export_all_and_report_ambiguous():
    chats = [
        _chat("a@chatroom", "同名群"),
        _chat("b@chatroom", "同名群"),
    ]
    selected, missing, ambiguous = _resolve_chat_targets(chats, ["同名群"])
    assert [x["username"] for x in selected] == ["a@chatroom", "b@chatroom"]
    assert missing == []
    assert ambiguous == [("同名群", ["a@chatroom", "b@chatroom"])]
