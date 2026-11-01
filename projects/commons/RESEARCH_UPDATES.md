# COMMONS research updates

## 22 October 2026 follow-up

COMMONS remains one of the main candidates at the user's request. The choice is provisional. Follow-up research found direct worker-product precedents in addition to the infrastructure competitors in the original proposal. The maintained proposal now includes them.

The most consequential technical finding is in OpenDP's source: its normal random-byte path uses OpenSSL; the alternative path is explicitly documented as non-secure. We must not disable security features merely to make a WASI build compile. Runtime and randomness integration need a defensible design before this project is considered ready to build.

[Full follow-up findings](../../research/search-round-2-2026-10-22/README.md) include source links, competing worker tools, current NEAR issue status and additional directions checked. The [original proposal snapshot](../../research/commons-2026-10-22/PROPOSAL.md) remains unchanged.
