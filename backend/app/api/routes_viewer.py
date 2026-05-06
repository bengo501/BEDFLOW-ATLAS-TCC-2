# endpoints para listar e servir malhas 3d ao visualizador web e ferramentas cli
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from bedflow_local_paths import (
    mesh_id_for_relative_path,
    project_root,
    resolve_validated_mesh_path,
    scan_project_mesh_files,
)

router = APIRouter()


class MeshInfo(BaseModel):
    mesh_id: str
    relative_path: str
    filename: str
    size_bytes: int
    mtime_iso: str
    format: str


class MeshListResponse(BaseModel):
    meshes: List[MeshInfo]
    total: int
    project_root_hint: str = Field(description="apenas informativo para o cli")


def _to_mesh_info(row: Dict[str, Any]) -> MeshInfo:
    ts = datetime.fromtimestamp(row["mtime"], tz=timezone.utc).isoformat()
    return MeshInfo(
        mesh_id=row["mesh_id"],
        relative_path=row["relative_path"],
        filename=row["filename"],
        size_bytes=int(row["size_bytes"]),
        mtime_iso=ts,
        format=str(row["format"]),
    )


@router.get("/viewer/meshes", response_model=MeshListResponse, tags=["viewer"])
async def list_viewer_meshes(
    q: Optional[str] = Query(None, description="filtro por nome ou caminho"),
    limit: int = Query(200, ge=1, le=2000),
):
    """
    inventario de malhas e cenas 3d geradas (stl, obj, ply, gltf, glb, blend)
    a partir de local_data e pastas legadas generated/.
    """
    rows = scan_project_mesh_files(max_files=limit * 4)
    if q:
        ql = q.strip().lower()
        rows = [
            r
            for r in rows
            if ql in r["relative_path"].lower() or ql in r["filename"].lower()
        ]
    rows = rows[:limit]
    root = project_root()
    return MeshListResponse(
        meshes=[_to_mesh_info(r) for r in rows],
        total=len(rows),
        project_root_hint=str(root),
    )


@router.get("/viewer/meshes/recent", response_model=MeshListResponse, tags=["viewer"])
async def list_recent_meshes(limit: int = Query(12, ge=1, le=100)):
    rows = scan_project_mesh_files(max_files=limit)
    root = project_root()
    return MeshListResponse(
        meshes=[_to_mesh_info(r) for r in rows],
        total=len(rows),
        project_root_hint=str(root),
    )


@router.get("/viewer/meshes/lookup", response_model=MeshInfo, tags=["viewer"])
async def lookup_mesh_by_id(mesh_id: str = Query(..., min_length=8, max_length=32)):
    for row in scan_project_mesh_files(max_files=2500):
        if row["mesh_id"] == mesh_id:
            return _to_mesh_info(row)
    raise HTTPException(status_code=404, detail="mesh nao encontrado")


@router.get("/viewer/mesh-stream", tags=["viewer"])
async def stream_mesh_file(
    path: Optional[str] = Query(
        None, description="caminho relativo ao repo (ex.: local_data/models_3d/x.stl)"
    ),
    mesh_id: Optional[str] = Query(None, description="alternativa ao path"),
):
    """
    serve bytes da malha depois de validar prefixo permitido (sem path traversal).
    """
    rel: Optional[str] = path
    if mesh_id and not rel:
        for row in scan_project_mesh_files(max_files=2500):
            if row["mesh_id"] == mesh_id:
                rel = row["relative_path"]
                break
    if not rel:
        raise HTTPException(status_code=400, detail="path ou mesh_id obrigatorio")
    p = resolve_validated_mesh_path(rel)
    if p is None:
        raise HTTPException(status_code=404, detail="ficheiro invalido ou inexistente")
    if path and mesh_id and mesh_id_for_relative_path(rel) != mesh_id:
        raise HTTPException(status_code=400, detail="mesh_id nao corresponde ao path")
    return FileResponse(
        path=str(p),
        filename=p.name,
        media_type="application/octet-stream",
    )
