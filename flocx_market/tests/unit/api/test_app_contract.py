import datetime
import json
from unittest import mock

import flocx_market.conf
from flocx_market.objects import bid, offer, contract
CONF = flocx_market.conf.CONF
now = datetime.datetime.utcnow()

contract_1_bid = bid.Bid(marketplace_bid_id='test_bid_1',
                         creator_bid_id="1234",
                         creator_id="2345",
                         server_quantity=2,
                         start_time=now,
                         end_time=now,
                         duration=16400,
                         status="available",
                         server_config_query={'foo': 'bar'},
                         cost=11.5
                         )

contract_2_bid = bid.Bid(marketplace_bid_id='test_bid_2',
                         creator_bid_id="2345",
                         creator_id="3456",
                         server_quantity=2,
                         start_time=now,
                         end_time=now,
                         duration=16400,
                         status="available",
                         server_config_query={'foo': 'bar'},
                         cost=11.5
                         )

contract_1_offer = offer.Offer(marketplace_date_created=now,
                               marketplace_offer_id='test_offer_1',
                               provider_id='1234',
                               creator_id='2345',
                               server_id='3456',
                               start_time=now,
                               end_time=now,
                               status='available',
                               server_config={'bar': 'foo'},
                               cost=0.0,
                               contract_id='test_contract_1'
                               )

contract_2_offer = offer.Offer(marketplace_offer_id='test_offer_2',
                               marketplace_date_created=now,
                               provider_id='2345',
                               creator_id='3456',
                               server_id='4567',
                               start_time=now,
                               end_time=now,
                               status='available',
                               server_config={'foo': 'bar'},
                               cost=0.0,
                               contract_id='test_contract_2'
                               )

test_contract_1 = contract.Contract(contract_id='test_contract_1',
                                    time_created=now,
                                    status='available',
                                    start_time=now,
                                    end_time=now,
                                    cost=0.0,
                                    bid_id=contract_1_bid.marketplace_bid_id,
                                    bid=None,
                                    )

test_contract_2 = contract.Contract(contract_id='test_contract_2',
                                    time_created=now,
                                    status='available',
                                    start_time=now,
                                    end_time=now,
                                    cost=0.0,
                                    bid_id=contract_2_bid.marketplace_bid_id,
                                    bid=None,
                                    )

test_contract_dict = dict(contract_id='test_contract_2',
                          time_created="2016-07-16T19:20:30",
                          status='available',
                          start_time="2016-07-16T19:20:30",
                          end_time="2016-07-16T19:20:30",
                          cost=0.0,
                          bid_id='test_bid_2',
                          offers=[contract_1_offer.marketplace_offer_id]
                          )


@mock.patch('flocx_market.objects.contract.Contract.get_all')
def test_get_contracts(mock_get_all, client):
    test_result = [test_contract_1, test_contract_2]
    mock_get_all.return_value = test_result
    response = client.get("/contract", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.json) == 2
    assert any(x['bid_id'] == test_contract_1.bid_id
               for x in response.json)
    assert any(x['bid_id'] == test_contract_2.bid_id
               for x in response.json)


@mock.patch('flocx_market.objects.contract.Contract.get')
def test_get_contract(mock_get, client):
    mock_get.return_value = test_contract_1
    response = client.get('/contract/{}'.format(
        test_contract_1.contract_id))
    assert response.status_code == 200
    mock_get.assert_called_with('test_contract_1')
    assert response.json['contract_id'] == 'test_contract_1'


@mock.patch('flocx_market.objects.contract.Contract.get')
def test_get_contract_missing(mock_get, client):
    mock_get.return_value = None
    response = client.get('/contract/does-not-exist')
    assert response.status_code == 404


@mock.patch('flocx_market.objects.contract.Contract.destroy')
@mock.patch('flocx_market.objects.contract.Contract.get')
def test_delete_contract(mock_get, mock_destroy, client):
    mock_get.return_value = test_contract_1
    response = client.delete('/contract/{}'.format(
        test_contract_1.contract_id))
    assert response.status_code == 200
    assert mock_destroy.call_count == 1


@mock.patch('flocx_market.objects.contract.Contract.get')
def test_delete_contract_missing(mock_get, client):
    mock_get.return_value = None
    response = client.delete('/contract/does-not-exist')
    assert response.status_code == 404


@mock.patch('flocx_market.objects.contract.Contract.create')
def test_create_contract(mock_create, client):
    mock_create.return_value = test_contract_1
    res = client.post('/contract', data=json.dumps(test_contract_dict))
    assert res.status_code == 201
    assert mock_create.call_count == 1
    assert res.json == test_contract_1.to_dict()


@mock.patch('flocx_market.objects.contract.Contract.save')
@mock.patch('flocx_market.objects.contract.Contract.get')
def test_update_contract(mock_get, mock_save, client):
    mock_get.return_value = test_contract_1
    mock_save.return_value = test_contract_1
    res = client.put('/contract/{}'.format(test_contract_1.contract_id),
                     data=json.dumps(dict(status='testing')))
    assert res.status_code == 200
    assert mock_save.call_count == 1
    assert res.json['status'] == 'testing'


@mock.patch('flocx_market.objects.contract.Contract.save')
@mock.patch('flocx_market.objects.contract.Contract.get')
def test_update_contract_missing(mock_get, mock_save, client):
    mock_get.return_value = None
    res = client.put('/contract/does-not-exist',
                     data=json.dumps(dict(status='testing')))
    assert res.status_code == 404
    assert mock_save.call_count == 0