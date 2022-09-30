def run_worker(things, stream=''):
    res = doStuff()
    return {'things': res, 'stream': stream}

if __name__ == '__main__':
    run_worker(
        [{
            'id': 0,
            'title': 'algotrading bot',
            'geo': 'us',
            'lang': 'en',
        },
        {
            'id': 1,
            'title': 'cryptocurrency robot',
            'geo': 'us',
            'lang': 'en',
        },
        {
            'id': 2,
            'title': 'crypto market trade',
            'geo': 'us',
            'lang': 'en',
        }],
        "some_stream"
    )
