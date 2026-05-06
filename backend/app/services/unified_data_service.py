from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.database import models, schemas
from backend.app.utils.pagination import build_paginated_payload, clean_filters, resolve_page_limit


class UnifiedDataService:
    """centraliza leituras para dashboard, historico e resultados."""

    @staticmethod
    def _to_public_file_url(relative_path: Optional[str]) -> Optional[str]:
        if not relative_path:
            return None
        normalized = str(relative_path).replace("\\", "/").lstrip("/")
        if normalized.startswith("local_data/"):
            return f"/files/{normalized[len('local_data/'):]}"
        if normalized.startswith("generated/"):
            return f"/generated/{normalized[len('generated/'):]}"
        if normalized.startswith("3d/") or normalized.startswith("models/"):
            return f"/generated/{normalized}"
        return None

    def _bed_to_model_3d(self, bed: models.Bed) -> schemas.Model3DResponse:
        blend_url = self._to_public_file_url(bed.blend_file_path)
        stl_url = self._to_public_file_url(bed.stl_file_path)
        return schemas.Model3DResponse(
            id=bed.id,
            user_id=bed.user_id,
            name=bed.name,
            description=bed.description,
            diameter=bed.diameter,
            height=bed.height,
            wall_thickness=bed.wall_thickness,
            particle_count=bed.particle_count,
            particle_diameter=bed.particle_diameter,
            particle_kind=bed.particle_kind,
            packing_method=bed.packing_method,
            porosity=bed.porosity,
            bed_file_path=bed.bed_file_path,
            json_file_path=bed.json_file_path,
            blend_file_path=bed.blend_file_path,
            stl_file_path=bed.stl_file_path,
            blend_file_url=blend_url,
            stl_file_url=stl_url,
            preview_model_url=blend_url or stl_url,
            has_model_files=bool(bed.blend_file_path or bed.stl_file_path),
            parameters_json=bed.parameters_json,
            created_at=bed.created_at,
            updated_at=bed.updated_at,
            created_by=bed.created_by,
        )

    def _simulation_query(
        self,
        db: Session,
        user_id: int,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
        bed_id: Optional[int] = None,
        regime: Optional[str] = None,
        solver: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ):
        query = db.query(models.Simulation).filter(models.Simulation.user_id == user_id)
        if bed_id is not None:
            query = query.filter(models.Simulation.bed_id == bed_id)
        if status:
            query = query.filter(models.Simulation.status == status)
        if regime:
            query = query.filter(models.Simulation.regime == regime)
        if solver:
            query = query.filter(models.Simulation.solver == solver)
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(
                (models.Simulation.name.ilike(like))
                | (models.Simulation.description.ilike(like))
            )
        if created_from:
            query = query.filter(models.Simulation.created_at >= created_from)
        if created_to:
            query = query.filter(models.Simulation.created_at <= created_to)
        return query

    def _models_query(
        self,
        db: Session,
        user_id: int,
        *,
        search: Optional[str] = None,
        packing_method: Optional[str] = None,
        has_blend: Optional[bool] = None,
        has_stl: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ):
        query = (
            db.query(models.Bed)
            .filter(models.Bed.user_id == user_id)
            .filter(
                (models.Bed.blend_file_path.isnot(None))
                | (models.Bed.stl_file_path.isnot(None))
            )
        )
        if search:
            like = f"%{search.strip()}%"
            query = query.filter(
                (models.Bed.name.ilike(like)) | (models.Bed.description.ilike(like))
            )
        if packing_method:
            query = query.filter(models.Bed.packing_method == packing_method)
        if has_blend is not None:
            if has_blend:
                query = query.filter(models.Bed.blend_file_path.isnot(None))
            else:
                query = query.filter(models.Bed.blend_file_path.is_(None))
        if has_stl is not None:
            if has_stl:
                query = query.filter(models.Bed.stl_file_path.isnot(None))
            else:
                query = query.filter(models.Bed.stl_file_path.is_(None))
        if created_from:
            query = query.filter(models.Bed.created_at >= created_from)
        if created_to:
            query = query.filter(models.Bed.created_at <= created_to)
        return query

    def list_models_3d(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 50,
        *,
        search: Optional[str] = None,
        packing_method: Optional[str] = None,
        has_blend: Optional[bool] = None,
        has_stl: Optional[bool] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> schemas.Model3DListResponse:
        page, limit, skip = resolve_page_limit(page=page, limit=limit)
        applied_filters = clean_filters(
            search=search,
            packing_method=packing_method,
            has_blend=has_blend,
            has_stl=has_stl,
            created_from=created_from.isoformat() if created_from else None,
            created_to=created_to.isoformat() if created_to else None,
        )
        query = self._models_query(
            db,
            user_id,
            search=search,
            packing_method=packing_method,
            has_blend=has_blend,
            has_stl=has_stl,
            created_from=created_from,
            created_to=created_to,
        ).order_by(models.Bed.updated_at.desc().nullslast(), models.Bed.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return schemas.Model3DListResponse(
            **build_paginated_payload(
                items=[self._bed_to_model_3d(bed) for bed in items],
                total=total,
                page=page,
                limit=limit,
                applied_filters=applied_filters,
            )
        )

    def get_history(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 100,
        *,
        entry_type: str = "all",
        search: Optional[str] = None,
        status: Optional[str] = None,
        packing_method: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> schemas.HistoryResponse:
        page, limit, skip = resolve_page_limit(page=page, limit=limit, max_limit=200)
        applied_filters = clean_filters(
            entry_type=entry_type if entry_type != "all" else None,
            search=search,
            status=status,
            packing_method=packing_method,
            created_from=created_from.isoformat() if created_from else None,
            created_to=created_to.isoformat() if created_to else None,
        )
        simulations = (
            []
            if entry_type == "model_3d"
            else self._simulation_query(
                db,
                user_id,
                search=search,
                status=status,
                created_from=created_from,
                created_to=created_to,
            )
            .order_by(models.Simulation.created_at.desc())
            .all()
        )
        model_beds = (
            []
            if entry_type == "simulation"
            else self._models_query(
                db,
                user_id,
                search=search,
                packing_method=packing_method,
                created_from=created_from,
                created_to=created_to,
            )
            .order_by(models.Bed.updated_at.desc().nullslast(), models.Bed.created_at.desc())
            .all()
        )

        history_items: list[schemas.HistoryEntryResponse] = []

        for sim in simulations:
            history_items.append(
                schemas.HistoryEntryResponse(
                    entry_type="simulation",
                    source_id=sim.id,
                    title=sim.name,
                    description=sim.description,
                    status=sim.status,
                    created_at=sim.created_at,
                    updated_at=sim.updated_at,
                    simulation_id=sim.id,
                    bed_id=sim.bed_id,
                    metadata={
                        "progress": sim.progress,
                        "case_directory": sim.case_directory,
                        "execution_time": sim.execution_time,
                    },
                )
            )

        for bed in model_beds:
            created_at = bed.updated_at or bed.created_at
            history_items.append(
                schemas.HistoryEntryResponse(
                    entry_type="model_3d",
                    source_id=bed.id,
                    title=bed.name,
                    description=bed.description,
                    created_at=created_at,
                    updated_at=bed.updated_at,
                    model_3d_id=bed.id,
                    bed_id=bed.id,
                    metadata={
                        "blend_file_path": bed.blend_file_path,
                        "stl_file_path": bed.stl_file_path,
                        "has_blend": bool(bed.blend_file_path),
                        "has_stl": bool(bed.stl_file_path),
                    },
                )
            )

        def sort_key(item: schemas.HistoryEntryResponse):
            dt = item.updated_at or item.created_at
            if dt is None:
                return datetime.min.replace(tzinfo=timezone.utc)
            return dt

        history_items.sort(key=sort_key, reverse=True)
        total = len(history_items)
        history_items = history_items[skip : skip + limit]

        return schemas.HistoryResponse(
            total=total,
            page=page,
            limit=limit,
            total_pages=build_paginated_payload(
                items=[],
                total=total,
                page=page,
                limit=limit,
            )["total_pages"],
            applied_filters=applied_filters,
            per_page=limit,
            pages=build_paginated_payload(
                items=[],
                total=total,
                page=page,
                limit=limit,
            )["pages"],
            simulations=[schemas.SimulationResponse.model_validate(sim) for sim in simulations],
            models_3d=[self._bed_to_model_3d(bed) for bed in model_beds],
            items=history_items,
        )

    def get_dashboard_summary(
        self,
        db: Session,
        user_id: int,
        recent_limit: int = 8,
    ) -> schemas.DashboardSummaryResponse:
        sim_query = self._simulation_query(db, user_id)
        counts_by_status = dict(
            sim_query.with_entities(models.Simulation.status, func.count(models.Simulation.id))
            .group_by(models.Simulation.status)
            .all()
        )
        metrics_row = sim_query.with_entities(
            func.count(models.Simulation.id),
            func.avg(models.Simulation.execution_time),
            func.avg(models.Simulation.pressure_drop),
            func.avg(models.Simulation.reynolds_number),
        ).first()
        recent_simulations = (
            sim_query.order_by(models.Simulation.created_at.desc()).limit(recent_limit).all()
        )
        recent_models = (
            self._models_query(db, user_id)
            .order_by(models.Bed.updated_at.desc().nullslast(), models.Bed.created_at.desc())
            .limit(recent_limit)
            .all()
        )

        by_status = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
        }
        for key in by_status:
            by_status[key] = int(counts_by_status.get(key, 0))

        total = int(metrics_row[0] or 0)
        completed = by_status["completed"]
        success_rate = (completed / total * 100.0) if total > 0 else 0.0

        return schemas.DashboardSummaryResponse(
            total_simulations=total,
            total_models_3d=self._models_query(db, user_id).count(),
            by_status=by_status,
            success_rate=success_rate,
            average_execution_time=float(metrics_row[1]) if metrics_row and metrics_row[1] is not None else None,
            average_pressure_drop=float(metrics_row[2]) if metrics_row and metrics_row[2] is not None else None,
            average_reynolds_number=float(metrics_row[3]) if metrics_row and metrics_row[3] is not None else None,
            recent_simulations=[
                schemas.SimulationResponse.model_validate(sim) for sim in recent_simulations
            ],
            recent_models_3d=[self._bed_to_model_3d(bed) for bed in recent_models],
        )
