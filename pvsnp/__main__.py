import sys
import uvicorn
from pvsnp.config import config


def main():
    reload = "--reload" in sys.argv
    uvicorn.run(
        "pvsnp.server:app",
        host=config.host,
        port=config.port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
