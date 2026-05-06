# servico de ingestao pos processamento
# localiza results json dentro da pasta do caso openfoam
# promove campos agregados para a linha simulation
# explode dicionarios metrics e fields em linhas result
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.database import crud, models, schemas


class ResultsService:
    def __init__(self) -> None:
        # quatro niveis: services -> app -> backend -> raiz do repositorio
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent

    def ingest_simulation_results(
        self,
        db: Session,
        simulation_id: int,
    ) -> Optional[models.Simulation]:
        """
        lê results.json do caso associado à Simulation e atualiza banco.

        - atualiza campos escalares em Simulation (queda de pressão, reynolds, etc.)
        - cria registros Result para métricas adicionais (bloco metrics)
        """
        sim = crud.SimulationCRUD.get(db, simulation_id)
        if not sim:
            return None

        if not sim.case_directory:
            return sim

        case_dir = (self.project_root / sim.case_directory).resolve()
        results_path = case_dir / "results.json"

        if not results_path.exists():
            return sim

        import json

        with results_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # simulation update recebe apenas chaves suportadas pelo schema pydantic
        sim_update = schemas.SimulationUpdate(
            status="completed",
            progress=100,
            mesh_cells_count=data.get("mesh_cells_count"),
            mesh_quality=data.get("mesh_quality"),
            case_directory=sim.case_directory,
            log_file_path=data.get("log_file", sim.log_file_path),
            pressure_drop=data.get("pressure_drop"),
            average_velocity=data.get("average_velocity"),
            reynolds_number=data.get("reynolds_number"),
            execution_time=data.get("execution_time", sim.execution_time),
            completed_at=data.get(
                "completed_at",
                datetime.now(timezone.utc),
            ),
        )

        sim = crud.SimulationCRUD.update(db, simulation_id, sim_update) or sim

        metrics_block = data.get("metrics", {})
        results_to_create: list[schemas.ResultCreate] = []

        for name, metric in metrics_block.items():
            if not isinstance(metric, dict):
                continue
            results_to_create.append(
                schemas.ResultCreate(
                    simulation_id=simulation_id,
                    result_type="metric",
                    name=name,
                    value=metric.get("value"),
                    unit=metric.get("unit"),
                    data_json=metric.get("data_json"),
                    file_path=None,
                    file_type=None,
                    timestep=metric.get("timestep"),
                )
            )

        fields_block = data.get("fields", {})
        for name, field in fields_block.items():
            if not isinstance(field, dict):
                continue
            results_to_create.append(
                schemas.ResultCreate(
                    simulation_id=simulation_id,
                    result_type=field.get("result_type", "field"),
                    name=name,
                    value=None,
                    unit=None,
                    data_json=field.get("data_json"),
                    file_path=field.get("file_path"),
                    file_type=field.get("file_type"),
                    timestep=field.get("timestep"),
                )
            )

        if results_to_create:
            crud.ResultCRUD.create_bulk(db, results_to_create)

        return sim

