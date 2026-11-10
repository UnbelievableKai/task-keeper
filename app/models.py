from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

# 할 일과 태그는 다대다 관계입니다.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # 기본은 lazy 로딩(select)입니다. 단건 조회에는 추가 쿼리가 1번뿐이라 문제없지만,
    # 목록 조회는 task마다 쿼리가 나가므로(N+1) task_service.list_tasks()에서
    # selectinload(Task.tags)로 한 번에 가져옵니다.
    tags = relationship("Tag", secondary=task_tags, lazy="select")
