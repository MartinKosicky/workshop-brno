import hashlib
import uuid

max_partitions = 5

all_uuids = [str(uuid.uuid4()) for _ in range(100)]

def hash_modulod(pk, parts=None):
    try:
        if parts is None:
            parts = max_partitions
        m = hashlib.md5()
        m.update(pk.encode())
        b = int.from_bytes(m.digest(), 'big', signed=False) % parts
        return all_uuids[b]

    except Exception as ex:
        print("hahaha")
        raise



def game_installed(agent_id, agent_name, game_name ):
    if not isinstance(game_name, str):
        raise ValueError("GameName must be str")

    return {
        "type":"GameInstalled",
        "agent_id":agent_id,
        "agent_name":agent_name,
        "game_name":game_name,
        "partition_key":hash_modulod(agent_id)
    }

def game_uninstalled(agent_id, agent_name, game_name):
    return {
        "type": "GameUninstalled",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "game_name": game_name,
        "partition_key": hash_modulod(agent_id)
    }

def game_installed_by_name(agent_id, game_name):
    return {
        "type":"GameInstalledByName",
        "agent_id":agent_id,
        "game_name":game_name,
        "partition_key":hash_modulod(game_name,10),
    }

def game_uninstalled_by_name(agent_id, game_name):
    return {
        "type": "GameUninstalledByName",
        "agent_id": agent_id,
        "game_name": game_name,
        "partition_key": hash_modulod(game_name,10),
    }