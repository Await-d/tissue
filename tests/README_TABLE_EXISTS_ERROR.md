# 解决 "table already exists" 错误

## 问题原因

当运行 pytest 测试时出现以下错误：

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table actor_subscribe already exists
```

这通常是由以下原因导致的：

1. **使用了持久化数据库**：测试使用的是文件数据库而不是内存数据库
2. **fixture scope 设置不当**：使用 `scope='session'` 或 `scope='module'` 导致多个测试共享数据库
3. **没有正确清理**：测试结束后没有删除表或关闭数据库连接
4. **重复调用 create_all**：在同一个数据库上多次调用 `create_all` 而没有先 `drop_all`

## 解决方案

### 1. 正确的 Fixture 配置（推荐）

在 `tests/conftest.py` 中配置：

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.base import Base

@pytest.fixture(scope='function')
def db_session():
    """为每个测试创建独立的内存数据库"""
    # 使用内存数据库
    engine = create_engine('sqlite:///:memory:', echo=False)

    # 创建所有表
    Base.metadata.create_all(engine)

    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(engine)
        engine.dispose()
```

### 2. 关键点说明

#### ✅ 使用 `scope='function'`

```python
@pytest.fixture(scope='function')  # ✅ 每个测试独立数据库
def db_session():
    pass

# ❌ 避免使用
@pytest.fixture(scope='session')   # ❌ 所有测试共享数据库
@pytest.fixture(scope='module')    # ❌ 模块内共享数据库
```

#### ✅ 使用内存数据库

```python
# ✅ 推荐：内存数据库，每次都是全新的
engine = create_engine('sqlite:///:memory:')

# ❌ 避免：文件数据库，可能有残留数据
engine = create_engine('sqlite:///test.db')
```

#### ✅ 正确清理

```python
try:
    yield session
finally:
    session.close()           # 关闭会话
    Base.metadata.drop_all(engine)  # 删除所有表
    engine.dispose()          # 释放引擎
```

### 3. 测试示例

```python
def test_example(db_session):
    """正确的测试写法"""
    # 创建记录
    actor = ActorSubscribe(
        actor_name='测试',
        from_date=date.today(),
        is_hd=True,
        is_zh=True,
        is_uncensored=False
    )
    db_session.add(actor)
    db_session.commit()

    # 验证
    result = db_session.query(ActorSubscribe).first()
    assert result is not None
```

### 4. 验证隔离性

运行以下测试来验证每个测试之间的隔离：

```python
def test_first(db_session):
    db_session.add(Torrent(hash='1', num='T-001'))
    db_session.commit()
    assert db_session.query(Torrent).count() == 1

def test_second(db_session):
    # 应该看到空数据库
    assert db_session.query(Torrent).count() == 0
```

## 常见错误模式

### ❌ 错误 1：直接创建引擎

```python
# ❌ 不推荐
def test_something():
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)  # 如果表已存在会报错
```

### ❌ 错误 2：共享数据库

```python
# ❌ 所有测试共享，容易冲突
@pytest.fixture(scope='session')
def db_session():
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)  # 第二次运行会报错
```

### ❌ 错误 3：不清理

```python
# ❌ 没有 finally 清理
@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    # 缺少清理代码
```

## 高级配置

如果需要共享数据库以提高速度，使用事务回滚：

```python
@pytest.fixture(scope='session')
def shared_engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def db_session(shared_engine):
    connection = shared_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()  # 回滚事务，清理数据
    connection.close()
```

## 运行测试

```bash
# 运行测试
pytest tests/test_example.py -v

# 查看详细输出
pytest tests/test_example.py -v -s

# 运行并查看 SQL
pytest tests/test_example.py -v -s --log-cli-level=DEBUG
```

## 参考文件

- `tests/conftest.py` - Fixture 配置
- `tests/test_example.py` - 示例测试
