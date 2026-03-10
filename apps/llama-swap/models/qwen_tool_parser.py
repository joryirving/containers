#!/usr/bin/env python3
import json
import re
import uuid
from typing import Any, Dict, List


TOOL_BLOCK_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL | re.IGNORECASE)
FUNCTION_RE = re.compile(r"<function=([a-zA-Z0-9_.:-]+)>(.*?)</function>", re.DOTALL | re.IGNORECASE)
PARAM_RE = re.compile(r"<parameter=([a-zA-Z0-9_.:-]+)>(.*?)</parameter>", re.DOTALL | re.IGNORECASE)


def _clean(text: str) -> str:
    return text.strip().replace("\r\n", "\n").strip()


def _new_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": f"call_{uuid.uuid4().hex[:12]}",
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps(args, ensure_ascii=False),
        },
    }


def _parse_json_style(block: str) -> Dict[str, Any] | None:
    raw = _clean(block)
    try:
        obj = json.loads(raw)
    except Exception:
        return None

    if not isinstance(obj, dict):
        return None

    name = obj.get("name")
    args = obj.get("arguments", {})

    if not isinstance(name, str) or not name:
        return None

    if not isinstance(args, dict):
        args = {"value": args}

    return _new_tool_call(name, args)


def _parse_xml_style(block: str) -> Dict[str, Any] | None:
    fm = FUNCTION_RE.search(block)
    if not fm:
        return None

    fn_name = _clean(fm.group(1))
    fn_body = fm.group(2)

    if not fn_name:
        return None

    args: Dict[str, Any] = {}
    for pm in PARAM_RE.finditer(fn_body):
        key = _clean(pm.group(1))
        val = _clean(pm.group(2))
        if not key:
            continue

        if key in args:
            if not isinstance(args[key], list):
                args[key] = [args[key]]
            args[key].append(val)
        else:
            args[key] = val

    return _new_tool_call(fn_name, args)


def parse_tool_calls(content: str) -> List[Dict[str, Any]]:
    if not content:
        return []

    tool_calls: List[Dict[str, Any]] = []

    for m in TOOL_BLOCK_RE.finditer(content):
        block = m.group(1)

        parsed = _parse_json_style(block)
        if parsed is None:
            parsed = _parse_xml_style(block)

        if parsed is not None:
            tool_calls.append(parsed)

    return tool_calls


if __name__ == "__main__":
    import sys

    input_text = sys.stdin.read()
    print(json.dumps({"tool_calls": parse_tool_calls(input_text)}, ensure_ascii=False, indent=2))
