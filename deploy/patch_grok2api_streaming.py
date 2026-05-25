#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


TARGET_PATH = Path(
    os.getenv(
        "GROK2API_IMAGE_SERVICE_PATH",
        "/app/app/services/grok/services/image.py",
    )
)
PATCH_MARKER = "Patched by grok-register: app-chat image streaming can stall"

OLD_BLOCK = """                    try:
                        try:
                            result = await self._stream_app_chat(
                                token_mgr=token_mgr,
                                token=current_token,
                                model_info=model_info,
                                prompt=prompt,
                                n=n,
                                response_format=response_format,
                                enable_nsfw=enable_nsfw,
                                chat_format=chat_format,
                            )
                        except UpstreamException as app_chat_error:
                            if rate_limited(app_chat_error):
                                raise
                            logger.warning(
                                "App-chat image stream failed, falling back to ws_imagine: %s",
                                app_chat_error,
                            )
                            result = await self._stream_ws(
                                token_mgr=token_mgr,
                                token=current_token,
                                model_info=model_info,
                                prompt=prompt,
                                n=n,
                                response_format=response_format,
                                size=size,
                                aspect_ratio=aspect_ratio,
                                enable_nsfw=enable_nsfw,
                                chat_format=chat_format,
                            )
                        async for chunk in result.data:
                            yielded = True
                            yield chunk
                        return"""

NEW_BLOCK = """                    try:
                        # Patched by grok-register: app-chat image streaming can stall
                        # without yielding image events, so prefer ws_imagine here.
                        result = await self._stream_ws(
                            token_mgr=token_mgr,
                            token=current_token,
                            model_info=model_info,
                            prompt=prompt,
                            n=n,
                            response_format=response_format,
                            size=size,
                            aspect_ratio=aspect_ratio,
                            enable_nsfw=enable_nsfw,
                            chat_format=chat_format,
                        )
                        async for chunk in result.data:
                            yielded = True
                            yield chunk
                        return"""


def main() -> int:
    if not TARGET_PATH.exists():
        print(f"[patch] target not found: {TARGET_PATH}", file=sys.stderr)
        return 1

    source = TARGET_PATH.read_text(encoding="utf-8")
    if PATCH_MARKER in source:
        print(f"[patch] already applied: {TARGET_PATH}")
        return 0

    if OLD_BLOCK not in source:
        print(f"[patch] expected stream block not found in {TARGET_PATH}", file=sys.stderr)
        return 1

    updated = source.replace(OLD_BLOCK, NEW_BLOCK, 1)
    TARGET_PATH.write_text(updated, encoding="utf-8")
    print(f"[patch] patched stream path in {TARGET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
