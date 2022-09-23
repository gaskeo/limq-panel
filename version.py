import os

VERSION = 'v1.0.3'


if not os.getenv('HOSTNAME'):
    raise EnvironmentError('Hostname not found')

hostname = os.getenv('HOSTNAME')

version = f"limq-panel/{VERSION}-{hostname}"


