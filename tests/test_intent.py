from agent_system.intent import RuleBasedClassifier, extract_session_id, get_classifier


def test_extract_session_id():
    assert extract_session_id("register for S5") == "S5"
    assert extract_session_id("sign me up for s12 please") == "S12"
    assert extract_session_id("recommend sessions") is None


def test_rule_based_intents():
    c = RuleBasedClassifier()
    assert c.classify("register for S5").name == "register"
    assert c.classify("recommend sessions").name == "recommend"
    assert c.classify("when is the event?").name == "faq"
    assert c.classify("how do I register?").name == "faq"   # question, not action
    assert c.classify("asdfqwer").name == "unknown"


def test_register_intent_extracts_entity():
    c = RuleBasedClassifier()
    intent = c.classify("please register for S5")
    assert intent.name == "register"
    assert intent.entities.get("session_id") == "S5"


def test_get_classifier_defaults_to_rule_based(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert isinstance(get_classifier(), RuleBasedClassifier)
