from datetime import datetime, timedelta
import pytest
import unittest.mock as mock

from oslo_db.exception import DBError
from oslo_context import context as ctx

from flocx_market.db.sqlalchemy import api
from flocx_market.common import exception as e
from flocx_market.common import statuses
from flocx_market.resource_objects import resource_types

now = datetime.utcnow()

test_offer_data = dict(
    status=statuses.AVAILABLE,
    project_id='1234',
    resource_id='4567',
    resource_type=resource_types.IRONIC_NODE,
    start_time=now - timedelta(days=1),
    end_time=now + timedelta(days=1),
    config={'foo': 'bar'},
    cost=0.0,
    )

test_offer_data_2 = dict(
    status=statuses.EXPIRED,
    project_id='1234',
    resource_id='456789',
    resource_type=resource_types.IRONIC_NODE,
    start_time=now - timedelta(days=2),
    end_time=now - timedelta(days=1),
    config={'foo': 'bar'},
    cost=0.0,
    )


test_offer_data_3 = dict(
    status=statuses.AVAILABLE,
    project_id='7788',
    resource_id='123',
    resource_type=resource_types.IRONIC_NODE,
    start_time=now - timedelta(days=2),
    end_time=now - timedelta(days=1),
    config={'foo': 'bar'},
    cost=0.0,
    )

test_bid_data_1 = dict(quantity=2,
                       start_time=now - timedelta(days=2),
                       end_time=now - timedelta(days=1),
                       duration=16400,
                       status=statuses.AVAILABLE,
                       config_query={'foo': 'bar'},
                       cost=11.5)


test_bid_data_2 = dict(quantity=2,
                       start_time=now - timedelta(days=2),
                       end_time=now + timedelta(days=1),
                       duration=16400,
                       status=statuses.AVAILABLE,
                       config_query={'foo': 'bar'},
                       cost=11.5)

test_bid_data_3 = dict(quantity=2,
                       start_time=now - timedelta(days=2),
                       end_time=now + timedelta(days=1),
                       duration=16400,
                       status=statuses.AVAILABLE,
                       config_query={'foo': 'bar'},
                       cost=11.5)

admin_context = ctx.RequestContext(is_admin=True)

scoped_context = ctx.RequestContext(is_admin=False,
                                    project_id='1234')

scoped_context_2 = ctx.RequestContext(is_admin=False,
                                      project_id='7788')


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_found(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    m = api.offer_create(test_offer_data, scoped_context)
    assert(api.offer_get(m.offer_id, scoped_context))


def test_offer_get_not_found(app, db, session):
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_get("NotHere", scoped_context)
    assert(excinfo.value.code == 404)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_found(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)
    api.offer_create(test_offer_data_3, scoped_context_2)

    assert len(api.offer_get_all(scoped_context)) == 3


def test_offer_get_all_none_found(app, db, session):
    assert (len(api.offer_get_all(scoped_context)) == 0)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_by_project_id(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)
    api.offer_create(test_offer_data_3, scoped_context_2)

    assert len(api.offer_get_all_by_project_id(scoped_context)) == 2


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_by_resource_id(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)

    assert len(api.offer_get_all_by_resource_id(
        scoped_context,
        test_offer_data["resource_id"])) == 1


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_by_resource_id_and_status(
        is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)

    assert len(api.offer_get_all_by_resource_id(
        scoped_context,
        test_offer_data["resource_id"],
        statuses.EXPIRED)) == 0


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_unexpired_admin(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)
    api.offer_create(test_offer_data_3, scoped_context_2)

    offers = api.offer_get_all_unexpired(admin_context)
    assert len(offers) == 2


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_get_all_unexpired_scoped(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    api.offer_create(test_offer_data_2, scoped_context)
    api.offer_create(test_offer_data_3, scoped_context_2)

    offers = api.offer_get_all_unexpired(scoped_context)
    assert len(offers) == 1


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_create(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)
    check = api.offer_get(offer.offer_id, scoped_context)

    assert check.to_dict() == offer.to_dict()


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_create_duplicate_resource_pass(
        is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    test_offer_data_expired = test_offer_data.copy()
    test_offer_data_expired["status"] = statuses.EXPIRED

    api.offer_create(test_offer_data_expired, scoped_context)
    api.offer_create(test_offer_data, scoped_context)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_create_duplicate_resource_fail(
        is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    api.offer_create(test_offer_data, scoped_context)
    with pytest.raises(ValueError):
        api.offer_create(test_offer_data, scoped_context)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_create_invalid_no_cost_admin(
        is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    data = dict(test_offer_data)
    del data['cost']

    with pytest.raises(DBError):
        api.offer_create(data, scoped_context)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_create_invalid_negative_cost_admin(
        is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    data = dict(test_offer_data)
    data['cost'] = -1

    with pytest.raises(ValueError):
        api.offer_create(data, scoped_context)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_delete_admin(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context_2)
    api.offer_destroy(offer.offer_id, admin_context)
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_get("NotHere", scoped_context)
    assert(excinfo.value.code == 404)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_delete_scoped_valid(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)
    api.offer_destroy(offer.offer_id, scoped_context)
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_get("NotHere", scoped_context)
    assert(excinfo.value.code == 404)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_delete_scoped_invalid(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)
    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.offer_destroy(offer.offer_id, scoped_context_2)
    assert(excinfo.value.code == 403)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_update_admin_valid(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)
    offer = api.offer_update(
        offer.offer_id,
        dict(status=statuses.EXPIRED),
        admin_context)
    check = api.offer_get(offer.offer_id, admin_context)

    assert check.status == statuses.EXPIRED


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_update_scoped_valid(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)
    offer = api.offer_update(
        offer.offer_id,
        dict(status=statuses.EXPIRED),
        scoped_context)
    check = api.offer_get(offer.offer_id, scoped_context)

    assert check.status == statuses.EXPIRED


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def test_offer_update_scoped_invalid(is_resource_admin, app, db, session):
    is_resource_admin.return_value = True
    offer = api.offer_create(test_offer_data, scoped_context)

    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.offer_update(
            offer.offer_id,
            dict(status=statuses.EXPIRED),
            scoped_context_2)
    assert(excinfo.value.code == 403)

    check = api.offer_get(offer.offer_id, scoped_context)
    assert check.status != statuses.EXPIRED


def test_bid_get(app, db, session):
    api.bid_create(test_bid_data_1, scoped_context)
    api.bid_create(test_bid_data_2, scoped_context)

    assert len(api.bid_get_all(admin_context)) == 2


def test_bid_get_all(app, db, session):
    api.bid_create(test_bid_data_1, scoped_context)
    api.bid_create(test_bid_data_2, scoped_context)

    assert len(api.bid_get_all(admin_context)) == 2


def test_bid_get_all_by_project_id(app, db, session):
    api.bid_create(test_bid_data_1, scoped_context)
    api.bid_create(test_bid_data_2, scoped_context)

    assert len(api.bid_get_all(admin_context)) == 2


def test_bid_get_all_unexpired(app, db, session):
    api.bid_create(test_bid_data_1, scoped_context)
    api.bid_create(test_bid_data_2, scoped_context)

    bids = api.bid_get_all(scoped_context)

    assert len(api.bid_get_all(scoped_context)) == 2
    assert len(api.bid_get_all_unexpired(scoped_context)) == 2

    api.bid_update(
        bids[1].bid_id,
        dict(status=statuses.EXPIRED),
        scoped_context)
    assert len(api.bid_get_all_unexpired(scoped_context)) == 1


def test_bid_create(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    check = api.bid_get(bid.bid_id, scoped_context)

    assert check.to_dict() == bid.to_dict()


def test_bid_create_invalid(app, db, session):
    data = dict(test_bid_data_1)
    del data['cost']

    with pytest.raises(DBError):
        api.bid_create(data, scoped_context)
    test_bid_data_1['creator_bid_id'] = '12a59a51-b4d6-497d-9f75-f56c409305c8'


def test_bid_delete_admin(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    api.bid_destroy(bid.bid_id, admin_context)
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.bid_get(bid.bid_id, scoped_context)
    assert(excinfo.value.code == 404)


def test_bid_delete_scoped_valid(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    api.bid_destroy(bid.bid_id, scoped_context)
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.bid_get(bid.bid_id, scoped_context)
    assert(excinfo.value.code == 404)


def test_bid_delete_scoped_invalid(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.bid_destroy(bid.bid_id, scoped_context_2)
    assert(excinfo.value.code == 403)
    assert (api.bid_get(bid.bid_id, scoped_context))


def test_bid_update_admin(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    bid = api.bid_update(
        bid.bid_id, dict(status=statuses.EXPIRED), admin_context)
    check = api.bid_get(bid.bid_id, scoped_context)

    assert check.status == statuses.EXPIRED


def test_bid_update_scoped_valid(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)
    bid = api.bid_update(
        bid.bid_id, dict(status=statuses.EXPIRED), scoped_context)
    check = api.bid_get(bid.bid_id, scoped_context)

    assert check.status == statuses.EXPIRED


def test_bid_update_scoped_invalid(app, db, session):
    bid = api.bid_create(test_bid_data_1, scoped_context)

    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.bid_update(
            bid.bid_id,
            dict(status=statuses.EXPIRED),
            scoped_context_2)
    assert(excinfo.value.code == 403)
    assert (api.bid_get(bid.bid_id, scoped_context).status
            != statuses.EXPIRED)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def create_test_contract_data(is_resource_admin):
    is_resource_admin.return_value = True
    bid = api.bid_create(test_bid_data_1, scoped_context)
    offer = api.offer_create(test_offer_data, scoped_context)

    contract_data = dict(
        time_created=now,
        status=statuses.AVAILABLE,
        start_time=now - timedelta(days=2),
        end_time=now - timedelta(days=1),
        cost=0.0,
        bid_id=bid.bid_id,
        offers=[offer.offer_id],
        project_id='5599'
    )

    return contract_data


def test_contract_get_all(app, db, session):
    contract_data = create_test_contract_data()
    api.contract_create(contract_data, admin_context)

    assert len(api.contract_get_all(scoped_context)) == 1


def test_contract_create_valid_admin(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)
    check = api.contract_get(contract.contract_id, admin_context)

    assert check.to_dict() == contract.to_dict()


def test_contract_create_invalid_admin(app, db, session):
    data = create_test_contract_data()
    del data['cost']
    with pytest.raises(DBError):
        api.contract_create(data, admin_context)


def test_contract_create_invalid_scoped(app, db, session):
    data = create_test_contract_data()
    with pytest.raises(e.RequiresAdmin) as excinfo:
        api.contract_create(data, scoped_context)
    assert(excinfo.value.code == 403)


def test_contract_delete_valid_admin(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)
    api.contract_destroy(contract.contract_id, admin_context)
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.contract_get(contract.contract_id, admin_context)
    assert(excinfo.value.code == 404)


def test_contract_delete_invalid_scoped(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)
    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.contract_destroy(contract.contract_id, scoped_context)
    assert (excinfo.value.code == 403)
    assert api.contract_get(contract.contract_id, admin_context)


def test_contract_update_valid_admin(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)
    contract = api.contract_update(
        contract.contract_id, dict(status=statuses.EXPIRED), admin_context)
    check = api.contract_get(contract.contract_id, admin_context)

    assert check.status == statuses.EXPIRED
    assert check.cost == 0.0


def test_contract_update_invalid_scoped(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)
    with pytest.raises(e.ResourceNoPermission) as excinfo:
        api.contract_update(
            contract.contract_id,
            dict(status=statuses.EXPIRED),
            scoped_context)
    assert (excinfo.value.code == 403)
    assert (api.contract_get(contract.contract_id, admin_context).status
            != statuses.EXPIRED)


def test_contract_get_all_unexpired(app, db, session):
    contract = api.contract_create(create_test_contract_data(), admin_context)

    assert len(api.contract_get_all_unexpired(admin_context)) == 1

    api.contract_update(contract.contract_id, dict(status=statuses.EXPIRED),
                        admin_context)
    assert (len(api.contract_get_all_unexpired(admin_context)) == 0)


@mock.patch('flocx_market.resource_objects.ironic_node'
            '.IronicNode.is_resource_admin')
def create_test_contract_data_for_ocr(is_resource_admin):
    is_resource_admin.return_value = True
    bid = api.bid_create(test_bid_data_1, scoped_context)
    offer = api.offer_create(test_offer_data, scoped_context)

    contract_data = dict(
        time_created=now,
        status=statuses.AVAILABLE,
        start_time=now - timedelta(days=2),
        end_time=now - timedelta(days=1),
        cost=0.0,
        bid_id=bid.bid_id,
        offers=[offer.offer_id],
        project_id='5599'
    )

    return contract_data, offer.offer_id


# contract_offer_relationship
def test_offer_contract_relationship_get_valid(app, db, session):
    contract_data, _ = create_test_contract_data_for_ocr()
    api.contract_create(contract_data, admin_context)
    ocr = api.offer_contract_relationship_get_all(admin_context)
    assert len(api.offer_contract_relationship_get_all(admin_context)) == 1
    assert (api.offer_contract_relationship_get(
        context=admin_context,
        offer_contract_relationship_id=ocr[0].offer_contract_relationship_id)
            .offer_contract_relationship_id ==
            ocr[0].offer_contract_relationship_id)


def test_offer_contract_relationship_get_invalid(app, db, session):
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_contract_relationship_get(
            context=admin_context,
            offer_contract_relationship_id="bad_id")
    assert (excinfo.value.code == 404)


def test_offer_contract_relationship_create_valid(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocr = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    assert contract.contract_id == ocr[0].contract_id


def test_offer_contract_relationship_create_invalid_scoped(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    with pytest.raises(e.RequiresAdmin) as excinfo:
        api.contract_create(contract_data, scoped_context)
    assert (excinfo.value.code == 403)


def test_offer_contract_relationship_delete_valid(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocrs = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    ocr_id = ocrs[0].offer_contract_relationship_id
    api.offer_contract_relationship_destroy(
        context=admin_context,
        offer_contract_relationship_id=ocr_id)

    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_contract_relationship_get(
            context=admin_context,
            offer_contract_relationship_id=ocr_id)
    assert (excinfo.value.code == 404)


def test_offer_contract_relationship_delete_invalid_scoped(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocrs = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    ocr_id = ocrs[0].offer_contract_relationship_id

    with pytest.raises(e.RequiresAdmin) as excinfo:
        api.offer_contract_relationship_destroy(
            context=scoped_context,
            offer_contract_relationship_id=ocr_id)
    assert (excinfo.value.code == 403)

    check = api.offer_contract_relationship_get(
        admin_context,
        ocr_id)
    assert check is not None


def test_offer_contract_relationship_delete_invalid_nonexistent(
        app, db, session):
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_contract_relationship_destroy(
            context=admin_context,
            offer_contract_relationship_id="bad_id")

    assert (excinfo.value.code == 404)


def test_offer_contract_relationship_update_valid(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocrs = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    ocr_id = ocrs[0].offer_contract_relationship_id

    api.offer_contract_relationship_update(
        context=admin_context,
        offer_contract_relationship_id=ocr_id,
        values=dict(status=statuses.EXPIRED))
    check = api.offer_contract_relationship_get(
        context=admin_context,
        offer_contract_relationship_id=ocr_id)

    assert check.status == statuses.EXPIRED
    assert check.offer_id == offer_test_id


@pytest.mark.skip(reason="we are currently not handling scoping correctly")
def test_offer_contract_relationship_update_invalid_scoped(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocrs = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    ocr_id = ocrs[0].offer_contract_relationship_id

    with pytest.raises(e.RequiresAdmin) as excinfo:
        api.offer_contract_relationship_update(
            context=scoped_context,
            offer_contract_relationship_id=ocr_id,
            values=dict(status=statuses.EXPIRED))
    assert (excinfo.value.code == 403)

    check = api.offer_contract_relationship_get(
        context=admin_context,
        offer_contract_relationship_id=ocr_id)

    assert check.status != statuses.EXPIRED
    assert check.offer_id == offer_test_id


def test_offer_contract_relationship_get_all_unexpired(app, db, session):
    contract_data, offer_test_id = create_test_contract_data_for_ocr()
    contract = api.contract_create(contract_data, admin_context)
    filters = {
        'offer_id': offer_test_id,
        'contract_id': contract.contract_id
    }
    ocrs = api.offer_contract_relationship_get_all(
        context=admin_context,
        filters=filters,
    )
    ocr_id = ocrs[0].offer_contract_relationship_id

    assert len(api.offer_contract_relationship_get_all_unexpired(
        admin_context)) == 1

    api.offer_contract_relationship_update(
        context=admin_context,
        offer_contract_relationship_id=ocr_id,
        values=dict(status=statuses.EXPIRED))
    assert len(api.offer_contract_relationship_get_all_unexpired(
        admin_context)) == 0


def test_offer_contract_relationship_update_invalid_nonexistent(
        app, db, session):
    with pytest.raises(e.ResourceNotFound) as excinfo:
        api.offer_contract_relationship_update(
            offer_contract_relationship_id="bad_id",
            values=dict(status=statuses.EXPIRED),
            context=admin_context)
    assert (excinfo.value.code == 404)
