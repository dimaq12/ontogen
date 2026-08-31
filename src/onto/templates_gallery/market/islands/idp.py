# ISLAND IdP (U4/D67): a static token table — a mock IdP for the exam.
# In the real world this would be OAuth/LDAP/whatever; it is grown by growisland like
# any island (intent+cases), and the membrane monitors its drift too.
_TOKENS = {
    "tok-alice-admin": ("admin", "alice"),
    "tok-bob": ("user", "bob"),
}


def authenticate(payload):
    tok = payload.get("token", "")
    if tok not in _TOKENS:
        raise KeyError("unknown token")
    role, subject = _TOKENS[tok]
    return {"role": role, "subject": subject}
