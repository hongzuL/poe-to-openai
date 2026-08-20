import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

from main import app  # noqa: E402  必须在 load_dotenv 之后导入

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "39527")),
        proxy_headers=True,
        forwarded_allow_ips=os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1"),
    )
