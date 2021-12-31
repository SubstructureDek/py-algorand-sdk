import base64
import json
import os
import urllib
import unittest
from datetime import datetime
from urllib.request import Request, urlopen
from algosdk.abi.base_type import ABIType
from algosdk.abi.contract import NetworkInfo

import parse
from behave import (
    given,
    when,
    then,
    register_type,
    step,
)  # pylint: disable=no-name-in-module

from algosdk.future import transaction
from algosdk import (
    abi,
    account,
    atomic_transaction_composer,
    encoding,
    error,
    mnemonic,
)
from algosdk.v2client import *
from algosdk.v2client.models import (
    DryrunRequest,
    DryrunSource,
    Account,
    Application,
    ApplicationLocalState,
)
from algosdk.error import AlgodHTTPError, IndexerHTTPError
from algosdk.testing.dryrun import DryrunTestCaseMixin
from algosdk.encoding import checksum

from test.steps.steps import token as daemon_token
from test.steps.steps import algod_port


####### Z's STEPS ########


def s512_256_uint64(witness):
    return int.from_bytes(checksum(witness)[:8], "big")


@then(
    "Ze atomic result at index {result_index} proves that randomness with input {input} was computed correctly for the ABI type."
)
def sha512_256_of_witness_mod_n_is_result(context, result_index, input):
    input = int.from_bytes(base64.decodebytes(input.encode()), "big")
    abi_type = ABIType.from_string("(uint64,byte[17])")
    result = context.atomic_transaction_composer_return.abi_results[
        int(result_index)
    ]
    rand_int, witness = abi_type.decode(result.raw_value)
    witness = bytes(witness)
    x = s512_256_uint64(witness)
    quotient = x % input
    assert quotient == rand_int