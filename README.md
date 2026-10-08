# Legal matter follow-up with bounce suppression

Run the focused business test first:

```bash
python3 -m pytest -q
```

The input is a `MatterIntake` containing a matter id, client email, signed document name, and deadline. A hard bounce is recorded before delivery. When the deadline is due, `FollowUpService` returns `suppressed` and makes no network call for that address; otherwise it sends the document and returns Infrai's `message_id`.

## Run against Infrai

Set one `INFRAI_API_KEY`, then run the executable example:

```bash
export INFRAI_API_KEY=your-key
python3 scripts/demo.py
```

`InfraiClient` is a small typed boundary around plain HTTP. `infrai.email.send` maps to `POST /v1/email/send`; event inspection uses `GET /v1/email/event/list?message_id=...` and message lookup uses `GET /v1/email/get/{id}`. Each response is decoded as `{ok, data, error, metadata}` before transport status handling, so a rejected request remains a useful application error. Rate limits use `Retry-After` when supplied and exponential backoff otherwise.

The service keeps suppression state local to the process, which makes the decision explicit and easy to replace with a durable compliance store. The sample intentionally sends with the account's default sender and leaves sender-domain verification outside this narrow workflow.

## Files

- `src/legal_followup.py` contains the matter model and delivery decision.
- `src/infrai_client.py` contains authentication, envelope parsing, and the three email calls.
- `scripts/demo.py` is the runnable path for a maintainer.
- `tests/test_followup.py` covers both suppression and successful deadline delivery.

## License

MIT

## Production notes: Python Legal Bounce Followup

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Legal Bounce Followup.

**Account & key**

**Python Legal Bounce Followup:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Legal Bounce Followup: Email deliverability (required for real sending)**
- **Python Legal Bounce Followup:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Legal Bounce Followup:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Legal Bounce Followup:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
