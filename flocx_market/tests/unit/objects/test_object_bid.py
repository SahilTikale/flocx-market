import datetime
import unittest.mock as mock

from oslo_context import context as ctx

from flocx_market.common import statuses
from flocx_market.objects import bid

now = datetime.datetime.utcnow()


test_bid_1 = dict(
    bid_id="123",
    creator_bid_id="1259a51-b4d6-497d-9f75-f56c409305c8",
    quantity=2,
    start_time=now,
    end_time=now,
    duration=16400,
    status=statuses.AVAILABLE,
    config_query={'foo': 'bar'},
    cost=11.2,
    project_id='5599',
    created_at=now,
    updated_at=now,
)

test_bid_2 = dict(
    bid_id="1232",
    creator_bid_id="12a59a51-b4d6-497d-9f75-f56c409305c8",
    quantity=2,
    start_time=now,
    end_time=now,
    duration=16400,
    status=statuses.AVAILABLE,
    config_query={'foo': 'bar'},
    cost=11.5,
    project_id='5599',
    created_at=now,
    updated_at=now,
)

scoped_context = ctx.RequestContext(is_admin=False,
                                    project_id='5599')


@mock.patch('flocx_market.db.sqlalchemy.api.bid_create')
def test_create(bid_create):
    bid_create.return_value = test_bid_1
    bid.Bid.create(test_bid_1, scoped_context)
    bid_create.assert_called_once()


@mock.patch('flocx_market.db.sqlalchemy.api.bid_get')
def test_get(bid_get):
    bid_get.return_value = test_bid_2
    b = bid.Bid(**test_bid_2)
    bid.Bid.get(b.bid_id, scoped_context)
    bid_get.assert_called_once()


def test_get_none():
    ret = bid.Bid.get(None, scoped_context)
    assert ret is None


@mock.patch('flocx_market.db.sqlalchemy.api.bid_get_all')
def test_get_all(bid_get_all):
    bid.Bid.get_all(scoped_context)
    bid_get_all.assert_called_once()


@mock.patch('flocx_market.db.sqlalchemy.api.bid_get_all_by_project_id')
def test_get_all_by_project_id(bid_get_all):
    bid.Bid.get_all_by_project_id(scoped_context)
    bid_get_all.assert_called_once()


@mock.patch('flocx_market.db.sqlalchemy.api.bid_destroy')
def test_destroy(bid_destroy):
    b = bid.Bid(**test_bid_1)
    b.destroy(scoped_context)
    bid_destroy.assert_called_once()


@mock.patch('flocx_market.db.sqlalchemy.api.bid_update')
def test_save(bid_update):
    bid_update.return_value = test_bid_1
    b = bid.Bid(**test_bid_1)
    b.status = statuses.EXPIRED
    b.save(scoped_context)
    bid_update.assert_called_once()


@mock.patch('flocx_market.objects.bid.Bid._from_db_object_list')
@mock.patch('flocx_market.objects.bid.db.bid_get_all_unexpired')
def test_update_to_expire(get_all, _from_db_object_list):
    bid.Bid.get_all_unexpired(scoped_context)

    get_all.assert_called_once()


@mock.patch('flocx_market.objects.bid.Bid.save')
def test_expire(save):
    o = bid.Bid(**test_bid_1)
    o.expire(scoped_context)

    save.assert_called_once()
