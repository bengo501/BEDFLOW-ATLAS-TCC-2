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
        import numpy as np
        import open3d as o3d
    except ImportError:
        print(
            "erro: instale as dependencias de visualizacao (open3d):\n"
            "  pip install -r requirements-visualizacao.txt\n"
            "(ficheiro na raiz do repo; no windows com caminhos longos desativados "
            "pode falhar — veja comentarios nesse ficheiro.)\n"
            "alternativa: visualizador web (three.js) ou blender.",
            file=sys.stderr,
        )
        return 2

    try:
        # enable_post_processing: triangula quads (comum em .obj do blender) e une vertices
        mesh = o3d.io.read_triangle_mesh(
            str(path), enable_post_processing=True, print_progress=False
        )
        if mesh.is_empty() or len(mesh.triangles) == 0:
            print(
                "erro: malha vazia apos leitura. o ficheiro pode ter so primitivas nao triangulares. "
                "tente exportar do blender com triangulate faces ou use .stl.",
                file=sys.stderr,
            )
            return 3
        # stl (e alguns exports) trazem vertex_colors brancas por vertice — len>0 impede
        # paint_uniform_color e a malha fica invisivel em fundo claro
        mesh.vertex_colors = o3d.utility.Vector3dVector()
        mesh.compute_vertex_normals()
        mesh.paint_uniform_color([0.12, 0.42, 0.78])

        bbox = mesh.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = float(np.max(bbox.get_extent()))
        if extent < 1e-12:
            print("erro: caixa limitadora degenerada (malha sem volume aparente).", file=sys.stderr)
            return 3

        win = f"bedflow viewer — {path.name}"
        # draw_geometries enquadra melhor a camara que Visualizer+reset_view_point (windows)
        try:
            o3d.visualization.draw_geometries(
                [mesh],
                window_name=win,
                width=1024,
                height=768,
                mesh_show_back_face=True,
                zoom=0.72,
                front=np.asarray([0.52, -0.62, -0.58]),
                lookat=center,
                up=np.asarray([0.0, 1.0, 0.0]),
            )
        except TypeError:
            o3d.visualization.draw_geometries(
                [mesh],
                window_name=win,
                width=1024,
                height=768,
                mesh_show_back_face=True,
            )
    except Exception as e:
        print(f"erro ao abrir malha: {e}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
