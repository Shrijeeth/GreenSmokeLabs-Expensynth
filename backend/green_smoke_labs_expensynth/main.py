import modal

app = modal.App(
    name=f"green-smoke-labs-expensynth",
)

DEPLOYMENT_IGNORE = [
    "__pycache__",
    ".venv",
    ".git",
    ".github",
    ".vscode",
    "*.env",
    "*.log",
    "*.egg-info",
    "build",
    ".ruff_cache",
]
image = modal.Image.debian_slim().pip_install_from_pyproject(
    pyproject_toml="pyproject.toml"
)
image = image.add_local_dir(
    ".",
    remote_path="/root/expensynth",
    ignore=DEPLOYMENT_IGNORE,
)


@app.function(image=image, secrets=[modal.Secret.from_name("expensynth")])
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def api_server():
    import sys

    sys.path.append("/root/expensynth")

    from fastapi import FastAPI, Request

    from green_smoke_labs_expensynth.api.router import api_router
    from green_smoke_labs_expensynth.lifecycle import shutdown, startup

    async def lifespan(wapp: FastAPI):
        await startup(wapp)
        yield
        await shutdown(wapp)

    web_app = FastAPI(lifespan=lifespan)
    web_app.include_router(api_router)

    return web_app
