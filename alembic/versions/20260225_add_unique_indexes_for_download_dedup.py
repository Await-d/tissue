from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect


revision: str = "20260225_add_download_uniqueness"
down_revision: Union[str, None] = "8b895bf9e393"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _get_existing_indexes(table_name: str) -> list[str]:
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        names = []
        for idx in inspector.get_indexes(table_name):
            name = idx.get("name")
            if isinstance(name, str):
                names.append(name)
        return names
    except Exception:
        return []


def _create_unique_index_if_missing(
    index_name: str, table_name: str, columns: list[str]
) -> None:
    if index_name not in _get_existing_indexes(table_name):
        op.create_index(index_name, table_name, columns, unique=True)


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    if index_name in _get_existing_indexes(table_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM torrent
        WHERE hash IS NOT NULL
          AND id NOT IN (
            SELECT MIN(id)
            FROM torrent
            WHERE hash IS NOT NULL
            GROUP BY hash
        )
        """
    )

    op.execute(
        """
        DELETE FROM actor_subscribe_download
        WHERE actor_subscribe_id IS NOT NULL
          AND num IS NOT NULL
          AND id NOT IN (
            SELECT MIN(id)
            FROM actor_subscribe_download
            WHERE actor_subscribe_id IS NOT NULL
              AND num IS NOT NULL
            GROUP BY actor_subscribe_id, num
        )
        """
    )

    _create_unique_index_if_missing("uq_torrent_hash", "torrent", ["hash"])
    _create_unique_index_if_missing(
        "uq_actor_subscribe_download_actor_num",
        "actor_subscribe_download",
        ["actor_subscribe_id", "num"],
    )


def downgrade() -> None:
    _drop_index_if_exists(
        "uq_actor_subscribe_download_actor_num", "actor_subscribe_download"
    )
    _drop_index_if_exists("uq_torrent_hash", "torrent")
