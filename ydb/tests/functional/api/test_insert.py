# -*- coding: utf-8 -*-
import logging

from hamcrest import assert_that, raises, equal_to

from ydb.tests.library.harness.kikimr_cluster import kikimr_cluster_factory
from ydb.tests.oss.ydb_sdk_import import ydb


logger = logging.getLogger(__name__)


class TestInsertOperations(object):
    @classmethod
    def setup_class(cls):
        cls.cluster = kikimr_cluster_factory()
        cls.cluster.start()
        cls.driver_config = ydb.DriverConfig(
            "%s:%s" % (cls.cluster.nodes[1].host, cls.cluster.nodes[1].port), database='/Root')
        cls.driver = ydb.Driver(cls.driver_config)
        cls.driver.wait()

    @classmethod
    def teardown_class(cls):
        if hasattr(cls, 'driver'):
            cls.driver.stop()

        if hasattr(cls, 'cluster'):
            cls.cluster.stop()

    def test_several_inserts_per_transaction_are_forbidden(self):
        # Arrange
        name = 'test_several_inserts_per_transaction_are_forbidden'
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, PRIMARY KEY(id));' % name)
        tx = session.transaction()

        tx.execute('INSERT INTO %s (id) VALUES (1);' % name)

        # Act + Assert
        def callee():
            tx.execute('insert into %s (id) values (2);' % name, commit_tx=True)

        assert_that(
            callee,
            raises(
                ydb.GenericError,
                "Data modifications previously made to table .*%s.* in current transaction won.*t be seen" % name,
            )
        )

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    0
                )
            )

    def test_insert_plus_update_per_transaction_are_forbidden(self):
        # Arrange
        name = "test_insert_plus_update_per_transaction_are_forbidden"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)
        session.transaction().execute(
            'insert into %s (id, value) values (1, 1), (2, 2), (3, 3);' % name, commit_tx=True)

        tx = session.transaction()
        # Act + Assert
        tx.execute('update %s set value = 4 where id = 3;' % name)

        def callee():
            tx.execute('insert into %s (id, value) values (4, 4);' % name)

        assert_that(
            callee,
            raises(
                ydb.GenericError,
                "Data modifications previously made to table .*%s.* in current transaction won.*t be seen" % name,
            )
        )

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    3
                )
            )

    def test_update_plus_insert_per_transaction_are_forbidden_prepared_case(self):
        # Arrange
        name = "test_update_plus_insert_per_transaction_are_forbidden_prepared_case"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)
        session.transaction().execute(
            'insert into %s (id, value) values (1, 1), (2, 2), (3, 3);' % name, commit_tx=True)

        # Act + Assert
        tx = session.transaction()
        tx.execute('update %s set value = 4 where id = 3;' % name)
        sql = 'insert into %s (id, value) values (4, 4);' % name
        prepared_sql = session.prepare(sql)

        def callee():
            tx.execute(prepared_sql)

        assert_that(
            callee,
            raises(
                ydb.GenericError,
                "Data modifications previously made to table .*%s.* in current transaction won.*t be seen" % name,
            )
        )

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    3
                )
            )

    def test_upsert_plus_insert_per_transaction_are_forbidden_prepared_case(self):
        name = "test_upsert_plus_insert_per_transaction_are_forbidden_prepared_case"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)
        session.transaction().execute(
            'insert into %s (id, value) values (1, 1), (2, 2), (3, 3);' % name, commit_tx=True)

        tx = session.transaction()
        tx.execute('upsert into %s (id, value) values (5, 5);' % name)

        def callee():
            tx.execute('insert into %s (id, value) values (4, 4);' % name, commit_tx=True)

        assert_that(
            callee,
            raises(
                ydb.GenericError,
                "Data modifications previously made to table .*%s.* in current transaction won.*t be seen" % name,
            )
        )

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    3
                )
            )

    def test_insert_plus_upsert_are_success(self):
        name = "test_insert_plus_upsert_are_success"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)
        session.transaction().execute(
            'insert into %s (id, value) values (1, 1), (2, 2), (3, 3);' % name, commit_tx=True)

        # Actually that should be ok since upsert is about blind writes
        with session.transaction() as tx:
            tx.execute('insert into %s (id, value) values (4, 4);' % name)
            tx.execute('upsert into %s (id, value) values (4, 5);' % name)
            tx.commit()

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    4
                )
            )

        with session.transaction() as tx:
            result_sets = tx.execute('select id, value from %s where id = 4;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].value,
                equal_to(
                    5
                )
            )

    def test_insert_revert_basis(self):
        name = "test_insert_revert_basis"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)
        session.transaction().execute(
            'insert into %s (id, value) values (1, 1), (2, 2), (3, 3);' % name, commit_tx=True)

        tx = session.transaction()
        tx.execute('insert or revert into %s (id, value) values (4, 4);' % name)

        def callee():
            tx.execute('insert or revert into %s (id, value) values (5, 5);' % name, commit_tx=True)

        assert_that(
            callee,
            raises(
                ydb.GenericError,
                "Data modifications previously made to table .*%s.* in current transaction won.*t be seen" % name,
            )
        )

        with session.transaction() as tx:
            result_sets = tx.execute('SELECT COUNT(*) as cnt FROM %s;' % name, commit_tx=True)
            assert_that(
                result_sets[0].rows[0].cnt,
                equal_to(
                    3
                )
            )

    def test_query_pairs(self):
        name = "test_insert_revert_basis"
        session = ydb.retry_operation_sync(lambda: self.driver.table_client.session().create())
        session.execute_scheme('CREATE TABLE %s (id Int32, value Int32, PRIMARY KEY(id));' % name)

        queries = (
            ('select count(*) as cnt from %s;', 'read'),
            ('insert into %s (id, value) values (4, 4)', 'read-write'),
            ('upsert  into %s (id, value) values (4, 4)', 'write'),
            ('replace into %s (id, value) values (4, 4)', 'write'),
            ('delete from %s;', 'read-write'),
            ('update %s set value = 4 where id = 2; ', 'read-write'),
            ('insert or revert into %s (id, value) values (4, 4);', 'read-write'),
        )

        for first_query, first_query_kind in queries:
            for second_query, second_query_kind in queries:
                tx = session.transaction()
                tx.execute(first_query % name)

                def callee():
                    tx.execute(second_query % name, commit_tx=True)

                if 'write' in first_query_kind and 'read' in second_query_kind:
                    assert_that(
                        callee,
                        raises(
                            ydb.GenericError,
                        )
                    )

                else:
                    callee()

                with session.transaction() as tx:
                    tx.execute(
                        'DELETE FROM %s;' % name, commit_tx=True)
