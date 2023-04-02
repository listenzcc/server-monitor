'''
File: app.py
Author: Chuncheng Zhang
Aim: Flask app

'''
# %%
from flask import Flask, request

from monitorloop.monitor import Monitor

# %%
app = Flask(__name__)

monitor = Monitor()
monitor.loop_update()

# %%


def serializable(list_of_dict):
    def convert(dct):
        d = dict()
        for key, value in dct.items():
            d[key] = '{}'.format(value)
        return d

    return [convert(e) for e in list_of_dict]


# %%


@app.route('/html/<page>')
def html(page):
    print('Request page {}'.format(page))
    return open('html/{}'.format(page)).read()


@app.route('/html/src/<src>')
def src(src):
    print('Request src {}'.format(src))
    return open('html/src/{}'.format(src)).read()


@app.route('/mongo/<page>')
def mongo(page):
    args = request.args
    print('Request page: {}'.format(page))
    print(args)

    if page == 'summary':
        return serializable(monitor.summary_mongo())

    if page == 'last':
        return serializable([monitor.checkout_mongo_by_id(e['last'])[0] for e in monitor.summary_mongo()])

    if page == 'fetchall':

        limit = 0
        if 'limit' in args:
            limit = int(args['limit'])

        sort_timestamp = 1
        if 'sort_timestamp' in args:
            sort_timestamp = int(args['sort_timestamp'])

        kwargs = dict(
            projection={'uptime': True,
                        'free': True,
                        'machineIP': True,
                        'timestamp': True},
            limit=limit,
            sort=[('timestamp', sort_timestamp)]
        )
        return serializable(monitor._find(**kwargs))

    return 'Can not find page: {}'.format(page)


# %%
if __name__ == '__main__':
    # Make sure the app is accessible for the remote client
    app.run(debug=True, host='0.0.0.0')

# %%
