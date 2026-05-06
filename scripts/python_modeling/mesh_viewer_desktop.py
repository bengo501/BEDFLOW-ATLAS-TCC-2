#!/usr/bin/env python3
"""
visualizador desktop minimalista para stl/obj/ply via open3d (opcional).
uso: python mesh_viewer_desktop.py caminho/absoluto/ou/relativo/modelo.stl
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="visualizador 3d simples (open3d)")
    p.add_argument("mesh_file", type=str, help="ficheiro .stl .obj ou .ply")
    args = p.parse_args()
    path = Path(args.mesh_file).expanduser().resolve()
    if not path.is_file():
        print(f"erro: ficheiro nao encontrado: {path}", file=sys.stderr)
        return 1
    suf = path.suffix.lower()
    if suf not in (".stl", ".obj", ".ply"):
        print(
            "erro: open3d neste script suporta stl, obj e ply. "
            "para gltf/glb use o visualizador web ou blender.",
            file=sys.stderr,
        )
        return 1
    try:
        import open3d as o3d
    except ImportError:
        print(
            "erro: instale open3d: pip install open3d\n"
            "alternativa: use o visualizador web (three.js) ou abra no blender.",
            file=sys.stderr,
        )
        return 2
    try:
        mesh = o3d.io.read_triangle_mesh(str(path))
        if mesh.is_empty():
            print("erro: malha vazia ou nao lida", file=sys.stderr)
            return 3
        mesh.compute_vertex_normals()
        o3d.visualization.draw_geometries(
            [mesh],
            window_name=f"bedflow viewer — {path.name}",
            width=1024,
            height=768,
        )
    except Exception as e:
        print(f"erro ao abrir malha: {e}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
