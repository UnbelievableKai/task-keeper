import pytest
from sqlalchemy import event

from app.services import task_service


def _count_queries(db_session, func):
    statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        func()
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
    return len(statements)


@pytest.mark.parametrize("task_count", [3, 10])
def test_list_tasks_query_count_is_constant(db_session, task_count):
    for i in range(task_count):
        task_service.create_task(db_session, f"할 일 {i}", ["개인", f"태그{i}"])
    # 로딩된 객체를 비워 실제 조회 쿼리가 나가도록 합니다.
    db_session.expire_all()

    def load_and_touch_tags():
        for task in task_service.list_tasks(db_session):
            _ = [tag.name for tag in task.tags]

    # tasks 1회 + tags 1회, 할 일 개수와 무관해야 합니다(N+1 방지).
    assert _count_queries(db_session, load_and_touch_tags) == 2
