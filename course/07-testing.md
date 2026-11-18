# Lesson 7: Testing with Postman and the regression runner

**Goal:** run all 32 scenarios three ways: Postman, a shell loop, and the regression runner that checks expected answers and records results.

## The test assets

```
scenarios/NN-name/
  endpoint.txt     POST /v1/systemone   (or /v1/decisions)
  request.json     ready to send; images embedded as base64
  response.json    the recorded reply
TESTING.md         every scenario: expected vs actual, request and response
postman/diffusiongemma-systemone.postman_collection.json
results/           run history (run-<timestamp>.json/.md, latest.md)
```

All of these are generated from one source of truth: the scenario list in `tools/build_collection.py`.

## Option A: Postman

1. **Import** `postman/diffusiongemma-systemone.postman_collection.json`.
2. Open the collection's **Variables** tab and set `baseUrl` to your endpoint, for example `http://<node-ip>:30810`. Leave `model` as `diffusiongemma`.
3. The collection is organised in folders, and the request names match the scenario folders:
   - `0. Basics`: health, models, chat completion
   - `1. Text decisions`: 01–14
   - `2. Document decisions`: 15–19
   - `3. Image decisions`: 20–30
   - `4. OpenAI-style /v1/decisions`: 31–32
4. Open a request:
   - **Body** is the request, exactly as in `request.json`.
   - **Examples** (the dropdown at the top right) holds the *recorded response*, so you can see the expected output without sending anything.
   - **Documentation** describes the scenario, its expected answers and its files.
5. Click **Send**. The **Tests** tab checks for HTTP 200. Open the console (View → Show Postman Console) to see each request's answers condensed.
6. Run everything: right-click the collection, choose **Run collection**, then **Run**.

## Option B: shell loop

```bash
export SYSONE_URL=http://<node-ip>:30810
for d in scenarios/*/; do
  printf '%-52s ' "$(basename $d)"
  curl -s $SYSONE_URL$(cut -d' ' -f2 $d/endpoint.txt) -H 'content-type: application/json' -d @$d/request.json \
    | jq -c '.answers | if type=="array" then map({(.name): (.choice // .probability)}) | add
                        else map_values(.choice // .noul // .score) end'
done
```

Compare a fresh reply with the recorded one:

```bash
d=scenarios/23-error-screenshot-incident-severity
diff <(jq -S '.answers | map_values(.choice // .noul // .score)' $d/response.json) \
     <(curl -s $SYSONE_URL/v1/systemone -H 'content-type: application/json' -d @$d/request.json \
       | jq -S '.answers | map_values(.choice // .noul // .score)')
```

Small probability differences are normal (see lesson 8). Look for changed labels.

## Option C: the regression runner

```bash
python3 tools/build_collection.py . --run $SYSONE_URL
```

The runner needs only Python 3 and the standard library. It:

1. rebuilds the Postman collection;
2. sends all 32 scenarios and compares each answer with its **expected** value;
3. rewrites `scenarios/*/request.json` and `response.json`, attaches each response to Postman as an example, and regenerates `TESTING.md`;
4. appends `results/run-<timestamp>.json` (full) and `.md` (summary), and updates `results/latest.md`.

Its output looks like this:

```
 0.13s  Support ticket triage: urgent=True(1.00)  team=infra(1.00)  severity=critical(1.00)
 ...
 0.15s  Invoice image vs purchase order (image + JSON): vendor_match=True(0.99)  over_po=False(0.00)  <-- expected True  action=hold(0.83)
 ...
expectations met: 77/78
```

The recorded baseline is **77/78 expectations met**, with a median latency of 0.17 s. The single miss is the cross-input number comparison explained in lesson 5.

## Add your own scenario

Add a scenario in `tools/build_collection.py` with the `ex(...)` helper:

```python
ex("1. Text decisions", "HR escalation",
   "Should this HR chat message go to a manager?",
   {"state": "My manager keeps scheduling me for 14-hour shifts and says I'll be fired if I complain.",
    "questions": {"escalate": noul("Should this be escalated to an HR manager?"),
                  "topic": choice("Topic", {"pay": None, "hours": "working time", "conduct": "behaviour", "leave": None})}},
   {"escalate": True, "topic": "hours"})
```

Then re-run the runner. Your scenario gets a folder, a Postman request and a `TESTING.md` entry, and it counts toward the expectation score.

## Use it in CI

Run the runner after every model, image or flag change. A drop below the baseline is a regression:

```bash
python3 tools/build_collection.py . --run $SYSONE_URL | tee run.log
grep -q "expectations met: 7[7-8]/78" run.log || { echo "regression"; exit 1; }
```

## Exercises

1. Run the collection in Postman and find the request with the slowest response.
2. Add two scenarios of your own, run the runner, and commit the new `scenarios/` folders.
3. Change `--gpu-memory-utilization` or `--max-num-seqs`, redeploy, and re-run. Did latency or accuracy change?

Next: [Lesson 8: Production tips and limits](08-production-tips.md)
