import asyncio
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

async def upload_once():
    """Upload new Splatoon 3 stats once using s3s script."""
    # Determine s3s script path
    base_dir = Path(__file__).parent.parent
    script_path = base_dir / 's3s' / 's3s.py'
    if not script_path.exists():
        logging.error(f"s3s script not found at {script_path}")
        return
    cmd = [sys.executable, str(script_path), '-r']
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(script_path.parent),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.error(f"s3s upload failed: {stderr.decode().strip()}")
    else:
        logging.info(f"s3s upload succeeded: {stdout.decode().strip()}")