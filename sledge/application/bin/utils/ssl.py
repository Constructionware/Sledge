
class SysCrypt:
    syskey:str = None

    def __init__(self):
        self.systemkey

    @property
    def platform(self):
        try:
            from platform import platform
            return platform().split('-')[0]  
        except ImportError:
            return None
        finally:
            del(platform)


    @property
    def uid(self):
        import subprocess, uuid
        try:       
            if self.platform == 'Windows':
                return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
            elif self.platform == 'Linux':
                return str(uuid.UUID(int=uuid.getnode())).split('-')[-1] 
            else:
                return str(uuid.uuid4())
        except Exception as e:
            print('sorry advanced code encountered ..', str(e))
            
        finally:
            del(subprocess)
            del(uuid)

    @property 
    def systemkey(self):
        try:
            from base64 import urlsafe_b64encode
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.hashes import SHA256
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from os import urandom

            passw = self.uid.encode()
            salt = urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt=salt,
                iterations=10000,
                backend=default_backend()
            )
            self.syskey = urlsafe_b64encode(kdf.derive(passw))
            return self.syskey
        except ImportError:
            return None
        finally:
            del(urlsafe_b64encode)
            del(default_backend)
            del(SHA256)
            del(PBKDF2HMAC)
            del(urandom)


scrp = SysCrypt()

#print(dir(platform))
#print(scrp.systemkey)