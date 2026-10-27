# Parameter dispatcher: ordinary parent-frame store contracts

This pass reconciles the dispatcher-related unresolved sites from the
[broad Thumb account](THUMB_STORE_PROVENANCE_REVIEW.md) using ordinary entry
`0x601C` and its active parent frame. Source is exact V2.8.4HF, 32,000 bytes,
SHA-256 `1ae519ba6194e8f7bdaaa94333a83a9e6fda3b0563f87f7d48383b37288c1780`.
The [artifact](../audit/data/dispatcher_store_context.json) records all 118
local stores, shared-frame transfers, explicit callee contracts and comparison
with the earlier original-handler execution examples. No firmware bytes change.

## BL does not always describe an ordinary returning call

The [remaining-handler review](REMAINING_AID_UPDATE_REVIEW.md) already documents
`0x6042`, `0x6048`, `0x604C` and loop entry `0x604E` as continuations using the
active `0x601C` frame. Eighteen BL sites transfer to these targets. They update
LR, but the continuation does not return to that new link. It continues the
handler loop and eventually unwinds the original parent frame.

The contextual CFG therefore transfers registers and stack facts to each of
those targets, with LR updated, and does not invent ordinary call fallthrough.
The four continuation entries are not independently seeded with arbitrary
registers/SP. Existing ordinary branches remain ordinary CFG edges. The final
BL at `0x6A44` no longer produces a supposed return into the following literal
area. The broader artifact now uses those same typed transfers too, while
retaining its independently seeded continuation entries. This improves its
fixed count from 791 to 805 and unresolved count from 111 to 97. No newly
classified store is relabeled as a firmware defect.

## Explicit callee and finite-set conditions

Nine ordinary callees have reviewed private-stack/fixed-global contracts used
to retain caller-frame facts: `0x4384`, `0x47B0`, `0x6B08`, `0x6B10`, `0x7128`,
`0x7138`, `0x7160`, `0x8574` and `0x8584`. This relies on valid nonaliasing
frames and their existing helper/runtime accounts. The artifact lists the
source-bound contract evidence. The receive routine `0x8038` has no such summary:
it writes caller-supplied count/list metadata, so stack-value facts are cleared.

Integer division additionally preserves R2/R3 under its reviewed contract;
only R0/R1 are treated as numeric outputs here. Numeric wrappers retain no
extra low-register preservation. In particular, a wrapper saving/restoring R3
before its tail transfer preserves an incoming operand, **not necessarily R3
on the eventual return**. Those two different contracts must not be conflated.

The optional abstract domain joins differing integer constants into finite
sets of at most 64 values. Larger joins widen to unknown; alternatives are
never truncated to force a bound. Mixed/unknown values remain unknown. The
analysis still explores both conditional branches and retains the prior
bounded dispatcher target-set assumptions. These address sets can include
infeasible combinations; they are conservative bounds, not exact path/value
correlations or validation-range proofs.

## Complete local result under this context

All 908 selected dispatcher starts are reached by the conservative contextual
CFG, covering the previously reviewed 1,882 instruction bytes. Its stores are:

| Classification | Store sites |
|---|---:|
| Fixed destination | 104 |
| Finite destination set | 10 |
| Entry-SP relative | 4 |
| Unresolved within this account | 0 |
| **Total** | **118** |

The common echo store `0x604C` has 16 destinations, the odd-byte addresses
`0x200C17..0x200C35`. Other shared stores select among refresh flags, echo
fields and derived knot words. Each set is listed individually. Treating a
common instruction as having one destination would lose these distinctions.

All **114 nonstack store sites** have observations in the earlier selector,
compound and remaining-handler artifacts; every recorded address and width fits
the contextual contract. Those handler fixtures use scripted receive metadata;
this comparison is not new physical or complete-transport admission evidence.
The four stack sites require the active valid parent frame.

This supplies caller-context address contracts for **41 sites** still unresolved
in the refined broader account. That broader pass has 97 unresolved rows under
its own entry assumptions; these contextual results do not rewrite its intrinsic/
general-entry status. The earlier broad CFG refinement accounts for another 14
sites without requiring the stronger single-parent-frame entry. Existing callback
and transitive artifacts reproduce byte for byte with the optional engine
features off; both updated artifacts reproduce in their new forms.

## Boundaries of the claim

No fixed/finite local destination overlaps `0x2005F0..0x2005F4`, assuming the
parent stack is disjoint from that word. This account excludes stores inside
receive/walker, default initializer and other callees; their separate contracts
must be composed before making a whole-ingest writer claim. Arbitrary entry
into a continuation without its parent frame remains outside this contract.

Register/frame preservation, dispatch bounds, immutable code and ordinary
entry conditions remain explicit. Global writer exclusion, asynchronous state,
DMA and parameter-to-output semantics remain wider work. The full goal is active.

```sh
python audit/tools/audit_dispatcher_store_context.py firmware_v2.8.4HF.bin --output audit/data/dispatcher_store_context.json
python -m unittest discover -s tests -t .
```

No device traffic, flashing, engine-setting change or hardware measurement occurred.
