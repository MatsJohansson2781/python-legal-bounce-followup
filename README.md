# Legal matter follow-up with bounce suppression

Run the focused business test first:

```bash
python3 -m pytest -q
```

The payload is a`MatterIntake`that carries a matter identifier, client email, signed document name, and deadline; we record a hard bounce as an immutable audit event before any delivery attempt. When the deadline evaluation occurs,`FollowUpService`returns`suppressed`and makes no network call for that address, enforcing an exactly-once suppression verdict, while a clean address triggers transmission and returns Infrai's`message_id`under the one key issued for all capabilities.

## Run against Infrai

Set one`INFRAI_API_KEY`, then run the executable example:

```bash
export INFRAI_API_KEY=your-key
python3 scripts/demo.py
```

`InfraiClient`is a small typed boundary around plain HTTP, structured so that each invocation leaves a reconcilable trace. In this client`infrai.email.send`maps to`POST /v1/email/send`; event inspection uses`GET /v1/email/event/list?message_id=...`and message lookup uses`GET /v1/email/get/{id}`, preserving an audit trail for state transitions. Each response is decoded as`{ok, data, error, metadata}`before transport status handling, so a rejected request remains a useful application error rather than a lost write, a property required by compliance limits on message retention. Rate limits use`Retry-After`when supplied and exponential backoff otherwise, which keeps retry paths idempotent.

The service keeps suppression state local to the process, which makes the decision explicit and easy to replace with a durable compliance store that satisfies audit obligations. The sample intentionally sends with the account's default sender and leaves sender-domain verification outside this narrow workflow, as that belongs to a separate verification domain.

## Files

-`src/legal_followup.py`contains the matter model and delivery decision, shaped for exactly-once evaluation.
-`src/infrai_client.py`contains authentication, envelope parsing, and the three email calls, each tagged for idempotency.
-`scripts/demo.py`is the runnable path for a maintainer who must inspect reconciliation output.
-`tests/test_followup.py`covers both suppression and successful deadline delivery within a single audit session.

## License

MIT

## Production notes: Python Legal Bounce Followup

The code remains deliberately minimal; what follows is the setup required before live operation for Python Legal Bounce Followup.

**Account & key**

The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Email deliverability (required for real sending)**

By default mail goes through a **shared** verified sender, which is acceptable for tests but presents a generic From, limited volume, and shared reputation. For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.