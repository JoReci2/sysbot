from ndcnApi.semaphore import Semaphore
from ndcnApi.vault import Vault
import json

def load(token, host):
    """
    Loads user environment variables from Semaphore and decrypts them using Vault.

    :param token: The authentication token for accessing Semaphore.
    :type token: str
    :param host: The host address for both Semaphore and Vault.
    :type host: str
    :return: A dictionary containing the decrypted user environment variables under the key ``user_env``.
    :rtype: dict
    :raises Exception: If any error occurs during the retrieval or decryption process.
    """
    semaphore = Semaphore(token, host, 3000, 'http')
    extra_var = json.loads(semaphore.env_get_extra_var("NDCN"))
    sealed_user_env = json.loads(semaphore.env_get("NDCN"))

    vault = Vault(host, 8200)
    result = vault.unvault_env(sealed_user_env, extra_var)
    return result
