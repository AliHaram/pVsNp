import uvicorn
from pvsnp.config import config

def main():
    uvicorn.run(
        "pvsnp.server:app",
        host=config.host,
        port=config.port,
        reload=True,
    )

if __name__ == "__main__":
    main()
