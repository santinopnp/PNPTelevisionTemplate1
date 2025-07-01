"""Simple utility to send or schedule broadcast messages."""

import asyncio
import argparse
from datetime import datetime, timezone

from bot.broadcast_manager import broadcast_manager


def parse_args():
    parser = argparse.ArgumentParser(description="Broadcast messages to users")
    parser.add_argument("--text", help="Text message")
    parser.add_argument("--photo", help="Path to photo to send")
    parser.add_argument("--video", help="Path to video to send")
    parser.add_argument("--animation", help="Path to GIF/animation")
    parser.add_argument("--parse-mode", default=None, help="Telegram parse mode")
    parser.add_argument("--language", help="Target language")
    parser.add_argument("--status", action="append", help="Target status")
    parser.add_argument(
        "--schedule",
        help="ISO timestamp to schedule (UTC). If omitted, send immediately",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    when = None
    if args.schedule:
        try:
            when = datetime.fromisoformat(args.schedule)
        except ValueError:
            print(f"Error: --schedule argument '{args.schedule}' is not a valid ISO timestamp.")
            exit(1)
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
    if when:
        broadcast_manager.schedule(
            when,
            text=args.text,
            parse_mode=args.parse_mode,
            photo=args.photo,
            video=args.video,
            animation=args.animation,
            language=args.language,
            statuses=args.status,
        )
        await asyncio.sleep(0.1)
    else:
        await broadcast_manager.send(
            text=args.text,
            parse_mode=args.parse_mode,
            photo=args.photo,
            video=args.video,
            animation=args.animation,
            language=args.language,
            statuses=args.status,
        )


if __name__ == "__main__":
    asyncio.run(main())
