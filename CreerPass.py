import base64
import time
import hashlib
import hmac
import pyotp

totp = pyotp.TOTP('CTXRHFP3VSZHIZR5WOJG3RYWCGZKSLVP')
totop_now = totp.now()
print(totop_now)
totp.verify(totop_now)
totp.verify('492039') # => False
#print(pyotp.random_base32())

def otpVerification():
    print("OTP verification")