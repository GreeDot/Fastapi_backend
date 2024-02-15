# alembic/env.py
import os
import sys
from pathlib import Path

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlalchemy import create_engine  # create_engine을 임포트합니다.

from app.models.models import Base  
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

aws_rds_id = os.getenv("AWS_RDS_ID")
aws_rds_password = os.getenv("AWS_RDS_PASSWORD")
sqlalchemy_url = f"mysql+pymysql://{aws_rds_id}:{aws_rds_password}@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedot"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    
    context.configure(
        url=sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario, we create an Engine using the provided database URL and associate a connection with the context.
    """
    # 직접 지정한 sqlalchemy_url을 사용하여 엔진을 생성합니다.
    connectable = create_engine(sqlalchemy_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
