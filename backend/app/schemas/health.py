from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    app_name: str
    app_version: str
    environment: str
    #: Which provider answers which question right now. A health probe that
    #: says "ok" while the reading role is quietly on the wrong endpoint is
    #: how a local-stack deployment ends up sending documents to the cloud.
    model_roles: dict[str, str]
