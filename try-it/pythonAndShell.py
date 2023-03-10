# %%
import json
import subprocess

# %%
cmd = 'ssh 172.18.116.146 ~/bin/uptimes-everything.sh'
plaintxt = subprocess.check_output(cmd, shell=True)
plaintxt = plaintxt.decode()

plaintxt
# %%
print(plaintxt)

# %%


def fetch_all(plaintxt):
    results = []

    queries = [e.strip() for e in plaintxt.split(
        '::---- New session for machine ----') if e.strip()]
    queries

    for query in queries:
        dct = dict()
        segments = [e.strip() for e in query.split('::----') if e.strip()]

        for seg in segments:
            head, body = seg.split('\n', 1)
            dct[head] = body

        results.append(dct)

    return results


dct = fetch_all(plaintxt)
dct

# %%
json.dump(dct, open('latest_results.json', 'w'))

# %%
