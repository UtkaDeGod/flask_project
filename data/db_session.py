import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None
__engine = None


def create_conn_args_string(login, password, host, port, db_name):
    return f'{login.strip()}:{password.rstrip()}@{host}:{port}/{db_name}'


def global_init(mode, conn_args_string):
    global __factory, __engine

    if __factory:
        return __engine

    if mode == 'sqlite':
        conn_str = f'sqlite:///{conn_args_string.strip()}?check_same_thread=False'
    elif mode == 'mysql':
        conn_str = f'mysql://{conn_args_string.strip()}'
    else:
        raise Exception('unknown type of base')
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, pool_size=50, max_overflow=0)
    __factory = orm.sessionmaker(bind=engine, autoflush=False)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)
    __engine = engine
    return __engine


def create_session() -> Session:
    global __factory
    return __factory()
