import logging
logger = logging.getLogger(__name__)

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from demo.app.config import DevelopmentConfig
from demo.app.models.snowflake import Base

@pytest.fixture(scope="session")
def connection():
    engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    connection = engine.connect()

    yield connection

    connection.close()

@pytest.fixture(scope="session")
def setup_db(connection, request):
    """
    Setup test database.

    Creates all database tables as declared in SQLAlchemy models,
    then proceeds to drop all the created tables after all tests
    have finished running.
    """
    Base.metadata.bind = connection
    Base.metadata.create_all()

    def teardown():
        Base.metadata.drop_all()

    request.addfinalizer(teardown)

    return None

@pytest.fixture(autouse=True)
def session(connection, setup_db, request):
    """
    Returns a database session to be used in a test.

    This fixture also alters the application's database
    connection to run in a transactional fashion. This means
    that all tests will run within a transaction, all database
    operations will be rolled back at the end of each test,
    and no test data will be persisted after each test.

    `autouse=True` is used so that session is properly
    initialized at the beginning of the test suite and
    factories can use it automatically.
    """
    transaction = connection.begin()
    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=connection))
    session.begin()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        """
        Support tests with rollbacks.

        This is required for tests that call some services that issue
        rollbacks in try-except blocks.

        With this event the Session always runs all operations within
        the scope of a SAVEPOINT, which is established at the start of
        each transaction, so that tests can also rollback the
        “transaction” as well while still remaining in the scope of a
        larger “transaction” that’s never committed.
        """
        if transaction.nested and not transaction._parent.nested:
            # ensure that state is expired the way session.commit() at
            # the top level normally does
            session.expire_all()
            session.begin()

    def teardown():
        session.remove()
        transaction.rollback()

    request.addfinalizer(teardown)

    return session
