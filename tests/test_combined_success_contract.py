def test_success_current_main_unavailable_contract(client, monkeypatch):
    monkeypatch.setattr('agents.success.routes.answer', lambda question: None)
    response = client.post('/api/success', json={'question': 'Campus support?'})
    assert response.status_code == 503
    assert isinstance(response.get_json()['error'], str)

def test_success_current_main_success_contract(client, monkeypatch):
    monkeypatch.setattr('agents.success.routes.answer', lambda question: 'Mocked campus support')
    response = client.post('/api/success', json={'question': 'Campus support?'})
    assert response.status_code == 200
    assert response.get_json() == {'reply': 'Mocked campus support', 'implemented': True}
