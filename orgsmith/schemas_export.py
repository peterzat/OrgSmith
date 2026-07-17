"""Emit the inter-stage contracts as JSON Schema.

`schemas.py` is the keystone: every contract between stages is a pydantic
model carrying an `orgsmith/<kind>@<ver>` id. Until now those shapes were
readable only by importing Python, which sits awkwardly against what the
airlock promises. A work order is a self-contained JSON file that *any*
author can answer -- that is the whole reason Python never calls a model --
and the promise is easier to keep when the shape of the file is published
rather than inferred from a pydantic class.

Models are **discovered, not listed**: anything carrying a `schema_id` is
emitted, and `run_emit_schemas` fails if `SCHEMA_IDS` names an id no model
claims. A new contract cannot be added and silently left out of the export,
which is the failure a hand-maintained registry invites.

Output is byte-stable (sorted keys) so re-emitting is a no-op and a test can
pin it, the same way the fleet's structure is pinned.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from . import schemas, state

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def contract_models() -> dict[str, type[BaseModel]]:
    """Every model carrying a `schema_id` default, keyed by that id."""
    found: dict[str, type[BaseModel]] = {}
    for module in (schemas, state):
        for obj in vars(module).values():
            if not (isinstance(obj, type) and issubclass(obj, BaseModel)):
                continue
            field = obj.model_fields.get("schema_id")
            if field is None or not isinstance(field.default, str):
                continue
            claimed = found.get(field.default)
            if claimed is not None and claimed is not obj:
                raise SystemExit(
                    f"two models claim schema id {field.default!r}: "
                    f"{claimed.__name__} and {obj.__name__}"
                )
            found[field.default] = obj
    return found


def schema_filename(schema_id: str) -> str:
    """`orgsmith/charter@1` -> `charter@1.json`."""
    return schema_id.split("/", 1)[1] + ".json"


def schema_document(model: type[BaseModel], schema_id: str) -> dict:
    doc = model.model_json_schema()
    doc["$schema"] = JSON_SCHEMA_DIALECT
    doc["$id"] = schema_id
    return doc


def render(schema_id: str, model: type[BaseModel]) -> str:
    return (
        json.dumps(
            schema_document(model, schema_id), indent=2, sort_keys=True
        )
        + "\n"
    )


def run_emit_schemas(out_dir: Path) -> int:
    models = contract_models()
    missing = set(schemas.SCHEMA_IDS.values()) - set(models)
    if missing:
        raise SystemExit(
            f"SCHEMA_IDS names ids no model claims: {sorted(missing)}"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    for schema_id, model in sorted(models.items()):
        (out_dir / schema_filename(schema_id)).write_text(
            render(schema_id, model), "utf-8"
        )
    print(f"emit-schemas: {len(models)} contracts -> {out_dir}")
    return 0
