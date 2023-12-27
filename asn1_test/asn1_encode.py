import asn1tools
import base64
import json
from binascii import a2b_hex

decode_json = {
    "devices": [
        {
            "manufacturer": "HUAWEI&XIAOMI",
            "hardwareType": "MCU",
            "hardwareVersion": "01",
            "softwareVersion": "000001"
        },
    ]
}

schema_all = asn1tools.compile_files('ans1.txt', 'uper')

schema_all.encode("devicestruct", decode_json)
