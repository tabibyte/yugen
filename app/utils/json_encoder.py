from flask.json.provider import JSONProvider
import numpy as np
import json

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        def default(o):
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            raise TypeError(f'Object of type {type(o)} is not JSON serializable')

        return json.dumps(obj, default=default, **kwargs)

    def loads(self, s: str | bytes, **kwargs):
        return json.loads(s, **kwargs)

    def _default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f'Object of type {type(o)} is not JSON serializable')