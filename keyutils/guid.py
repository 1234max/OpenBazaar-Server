__author__ = 'chris'

# pylint: disable=import-error
#import guidc
from binascii import hexlify, unhexlify

import nacl.signing
import nacl.hash

def _testpow(pow_hash):
    return True if int(pow_hash, 16) < 50 else False

class GUID(object):
    # pylint: disable=W0633
    def __init__(self, keys=None, use_C_lib=False):
        if keys is None:
            if use_C_lib:  # disabled for now
                # self.privkey = unhexlify(guidc.generate())
                self.privkey = None
                self.signing_key = nacl.signing.SigningKey(self.privkey)
                verify_key = self.signing_key.verify_key
                signed = self.signing_key.sign(str(verify_key))
                h = nacl.hash.sha512(signed)
                self.signed_pubkey = signed
                self.guid = unhexlify(h[:40])
            else:
                self.privkey = self.generate()
        else:
            self.signing_key, self.guid, self.signed_pubkey, self.privkey = keys

    def generate(self):
        valid_pow = False
        while not valid_pow:
            signing_key = nacl.signing.SigningKey.generate()
            verify_key = signing_key.verify_key
            signed = signing_key.sign(str(verify_key))
            h = nacl.hash.sha512(signed)
            pow_hash = h[64:128]
            valid_pow = _testpow(pow_hash[:6])
        self.signing_key = signing_key
        self.guid = unhexlify(h[:40])
        self.signed_pubkey = signed
        return signing_key.encode()

    @classmethod
    def from_privkey(cls, privkey):
        signing_key = nacl.signing.SigningKey(privkey)
        verify_key = signing_key.verify_key
        signed = signing_key.sign(str(verify_key))
        h = nacl.hash.sha512(signed)
        pow_hash = h[64:128]
        if _testpow(pow_hash[:6]):
            return GUID((signing_key, unhexlify(h[:40]), signed, privkey))

    def __str__(self):
        return "privkey: %s\nsigned pubkey: %s\nguid: %s" % (
            hexlify(self.privkey), hexlify(self.signed_pubkey), hexlify(self.guid))
