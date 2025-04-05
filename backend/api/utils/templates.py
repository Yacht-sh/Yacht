import re
from fastapi import HTTPException
from typing import Dict, List

# For Templates
REGEXP_PORT_ASSIGN = r"^(?:(?:\d{1,5}:)?\d{1,5}|:\d{1,5})/(?:tcp|udp)$"

# Input Format:
# [
#     '80:8080/tcp',
#     '123:123/udp'
#     '4040/tcp',
# ]
# Result Format:
# [
#     {
#         'cport': '80',
#         'hport': '8080',
#         'proto': 'tcp',
#     },
#     ...
# ]


def conv_ports2dict(data: List[str]) -> List[Dict[str, str]]:
    if len(data) > 0 and type(data[0]) == dict:
        delim = ":"
        portlst = []
        for port_data in data:
            for label, port in port_data.items():
                if not re.match(REGEXP_PORT_ASSIGN, port, flags=re.IGNORECASE):
                    raise HTTPException(
                        status_code=500,
                        detail="Malformed port assignment." + str(port_data),
                    )

                hport, cport = None, port
                if delim in cport:
                    hport, cport = cport.split(delim, 1)
                    if not hport:
                        hport = None
                cport, proto = cport.split("/", 1)
                portlst.append(
                    {"cport": cport, "hport": hport, "proto": proto, "label": label}
                )
            return portlst

    elif type(data) == list:
        delim = ":"
        portlst = []
        for port_data in data:
            if not re.match(REGEXP_PORT_ASSIGN, port_data, flags=re.IGNORECASE):
                raise HTTPException(
                    status_code=500, detail="Malformed port assignment." + port_data
                )

            hport, cport = None, port_data
            if delim in cport:
                hport, cport = cport.split(delim, 1)
                if not hport:
                    hport = None
            cport, proto = cport.split("/", 1)
            portlst.append({"cport": cport, "hport": hport, "proto": proto})
        return portlst
    else:
        return None


# Input Format:
# [
#     {
#         'net.ipv6.conf.all.disable_ipv6': '0'
#     }
# ]
# Result Format:
# [
#     {
#         'name': 'net.ipv6.conf.all.disable_ipv6',
#         'value': '0'
#     }
# ]


def conv_sysctls2dict(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{"name": k, "value": v} for item in data for k, v in item.items()]


def conv2dict(name, value):
    _tmp_attr = {name: value}
    return _tmp_attr
